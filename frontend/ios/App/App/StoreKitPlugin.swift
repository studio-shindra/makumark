import Foundation
import Capacitor
import StoreKit

@objc(StoreKitPlugin)
public class StoreKitPlugin: CAPPlugin {
    
    // 購入完了を監視するタスク
    private var updateListenerTask: Task<Void, Error>?
    
    override public func load() {
        // アプリ起動時にトランザクション監視を開始
        updateListenerTask = listenForTransactions()
    }
    
    deinit {
        updateListenerTask?.cancel()
    }
    
    // MARK: - Initialize (ダミー - StoreKit 2は自動初期化)
    @objc func initialize(_ call: CAPPluginCall) {
        call.resolve(["success": true])
    }
    
    // MARK: - Purchase Premium
    @objc func purchasePremium(_ call: CAPPluginCall) {
        guard let productId = call.getString("productId") else {
            call.reject("Product ID is required")
            return
        }
        
        Task {
            do {
                // 商品情報を取得
                let products = try await Product.products(for: [productId])
                guard let product = products.first else {
                    call.reject("Product not found")
                    return
                }
                
                // 購入実行
                let result = try await product.purchase()
                
                switch result {
                case .success(let verification):
                    // トランザクション検証
                    let transaction = try checkVerified(verification)
                    
                    // トランザクション完了
                    await transaction.finish()
                    
                    call.resolve([
                        "success": true,
                        "transactionId": transaction.id,
                        "productId": transaction.productID
                    ])
                    
                case .userCancelled:
                    call.reject("User cancelled the purchase")
                    
                case .pending:
                    call.reject("Purchase is pending")
                    
                @unknown default:
                    call.reject("Unknown purchase result")
                }
            } catch {
                call.reject("Purchase failed: \(error.localizedDescription)")
            }
        }
    }
    
    // MARK: - Restore Purchases
    @objc func restorePurchases(_ call: CAPPluginCall) {
        Task {
            do {
                // App Store から購入を同期
                try await AppStore.sync()
                
                // 現在の権限を確認
                let isPremium = await checkPremiumStatus()
                
                call.resolve([
                    "success": true,
                    "isPremium": isPremium
                ])
            } catch {
                call.reject("Restore failed: \(error.localizedDescription)")
            }
        }
    }
    
    // MARK: - Check Premium Status
    @objc func checkPremiumStatus(_ call: CAPPluginCall) {
        Task {
            let isPremium = await checkPremiumStatus()
            call.resolve([
                "isPremium": isPremium
            ])
        }
    }
    
    // MARK: - Helper: Check Premium Status
    private func checkPremiumStatus() async -> Bool {
        // すべての有効なサブスクリプションを取得
        var validSubscriptions: [Transaction] = []
        
        for await result in Transaction.currentEntitlements {
            guard case .verified(let transaction) = result else {
                continue
            }
            
            // サブスクリプションが有効か確認
            if transaction.revocationDate == nil {
                validSubscriptions.append(transaction)
            }
        }
        
        return !validSubscriptions.isEmpty
    }
    
    // MARK: - Helper: Transaction Verification
    private func checkVerified<T>(_ result: VerificationResult<T>) throws -> T {
        switch result {
        case .unverified:
            throw StoreError.failedVerification
        case .verified(let safe):
            return safe
        }
    }
    
    // MARK: - Helper: Listen for Transactions
    private func listenForTransactions() -> Task<Void, Error> {
        return Task.detached {
            for await result in Transaction.updates {
                guard case .verified(let transaction) = result else {
                    continue
                }
                
                // トランザクション完了
                await transaction.finish()
                
                // JS側に通知（オプション）
                // self.notifyListeners("transactionUpdate", data: ["transactionId": transaction.id])
            }
        }
    }
}

enum StoreError: Error {
    case failedVerification
}
