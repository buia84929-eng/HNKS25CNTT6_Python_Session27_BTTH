from abc import ABC, abstractmethod

class VNPayGateway:
    def execute_pay(self, account, amount):
        print(f"[Hệ thống VNPay]: Đang kết nối tới tài khoản {account.account_number}...")
        if account.withdraw(amount):
            return True
        return False

class ViettelMoneyGateway:
    def execute_pay(self, account, amount):
        print(f"[Hệ thống Viettel Money]: Đang xử lý giao dịch cho tài khoản {account.account_number}...")
        if account.withdraw(amount):
            return True
        return False

def process_payment(payment_gateway, account, amount):
    if not hasattr(payment_gateway, "execute_pay") or not callable(getattr(payment_gateway, "execute_pay")):
        print("Lỗi hệ thống: Cổng thanh toán không hợp lệ hoặc chưa được tích hợp phương thức thanh toán.")
        return False
    return payment_gateway.execute_pay(account, amount)

class BaseAccount(ABC):
    bank_name = "Vietcombank"

    def __init__(self, account_number, account_holder, initial_balance = 0.0):
        if not self.validate_account_number(account_number):
            print("Số tài khoản không hợp lệ! Phải gồm đúng 10 chữ số.")
            return
        self.account_number = account_number
        self._account_holder = ""
        self.account_holder = account_holder
        self.__balance = float(initial_balance)

    @property
    def balance(self):
        return self.__balance

    def _set_balance(self, amount):
        self.__balance = amount

    @property
    def account_holder(self):
        return self._account_holder

    @account_holder.setter
    def account_holder(self, name):
        self._account_holder = " ".join(name.strip().split()).upper()

    @abstractmethod
    def deposit(self, amount):
        pass

    @abstractmethod
    def withdraw(self, amount):
        pass

    def __add__(self, other):
        if not isinstance(other, BaseAccount):
            return "Lỗi: Đối tượng không phải là tài khoản hợp lệ"
        return self.balance + other.balance

    def __lt__(self, other):
        if not isinstance(other, BaseAccount):
            return False
        return self.balance < other.balance

    @staticmethod
    def validate_account_number(account_number):
        return isinstance(account_number, str) and account_number.isdigit() and len(account_number) == 10

    @classmethod
    def update_bank_name(cls, new_name):
        cls.bank_name = new_name

class SavingsAccount(BaseAccount):
    def __init__(self, account_number, account_holder, interest_rate, initial_balance = 0.0):
        super().__init__(account_number, account_holder, initial_balance)
        self.interest_rate = float(interest_rate)

    def deposit(self, amount):
        if amount <= 0:
            print("Số tiền nạp phải lớn hơn 0.")
            return False
        self._set_balance(self.balance + amount)
        return True

    def withdraw(self, amount):
        if amount <= 0:
            print("Số tiền rút phải lớn hơn 0.")
            return False
        penalty_fee = amount * 0.02
        total_deduction = amount + penalty_fee
        if self.balance >= total_deduction:
            self._set_balance(self.balance - total_deduction)
            print("Rút tiền thành công!")
            print(f"Số tiền rút: {amount:,.0f} VND")
            print(f"Phí phạt rút trước hạn (2%): {penalty_fee:,.0f} VND")
            return True
        print(f"Giao dịch thất bại! Số dư không đủ để trả cả tiền gốc lẫn phí phạt ({total_deduction:,.0f} VND).")
        return False

    def apply_interest(self):
        interest = self.balance * self.interest_rate
        old_balance = self.balance
        self._set_balance(old_balance + interest)
        return old_balance, interest, self.balance

class CreditAccount(BaseAccount):
    def __init__(self, account_number, account_holder, credit_limit, initial_balance = 0.0):
        super().__init__(account_number, account_holder, initial_balance)
        self.credit_limit = float(credit_limit)

    def deposit(self, amount):
        if amount <= 0:
            print("Số tiền nạp phải lớn hơn 0.")
            return False
        self._set_balance(self.balance + amount)
        return True

    def withdraw(self, amount):
        if amount <= 0:
            print("Số tiền rút phải lớn hơn 0.")
            return False
        if self.balance - amount < -self.credit_limit:
            print("Lỗi nghiệp vụ: Vượt quá hạn mức thấu chi cho phép!")
            return False
        self._set_balance(self.balance - amount)
        print("Rút tiền thành công! (Sử dụng hạn mức thấu chi)")
        print(f"Số tiền rút: {amount:,.0f} VND")
        return True

class DigitalPremiumMixin:
    def cashback_reward(self, amount):
        if amount > 5000000:
            return amount * 0.01
        return 0.0

class HybridAccount(SavingsAccount, DigitalPremiumMixin):
    def __init__(self, account_number, account_holder, interest_rate, initial_balance = 0.0):
        super().__init__(account_number, account_holder, interest_rate, initial_balance)

    def deposit(self, amount):
        if amount <= 0:
            print("Số tiền nạp phải lớn hơn 0.")
            return False
        success = super().deposit(amount)
        if success:
            cashback = self.cashback_reward(amount)
            if cashback > 0:
                self._set_balance(self.balance + cashback)
                print(f"[Ưu đãi Premium]: Bạn được hoàn tiền 1% ({cashback:,.0f} VND) vào tài khoản!")
        return success

def main():
    accounts = []
    current_account = None

    while True:
        print('''
===== VIETCOMBANK DIGIBANK PRO SIMULATOR =====
1. Mở tài khoản mới (Chọn loại tài khoản)
2. Xem thông tin & Kiểm tra thứ tự kế thừa (MRO)
3. Giao dịch Nạp / Rút tiền & Tính điểm thưởng (Đa hình)
4. Tích lũy / Áp dụng lãi suất định kỳ
5. Kiểm tra tính năng gộp tài khoản & So sánh (Overloading)
6. Thanh toán hóa đơn qua Cổng trung gian (Duck Typing)
7. Thoát chương trình
==============================================
''')
        choice = input("Chọn chức năng (1-7): ").strip()

        match choice:
            case "1":
                print("--- CHỌN LOẠI TÀI KHOẢN ---")
                print("1. Savings Account (Tài khoản Tiết kiệm)")
                print("2. Credit Account (Tài khoản Tín dụng)")
                print("3. Hybrid Account (Tài khoản Đa năng)")
                type_choice = input("Chọn loại tài khoản (1-3): ").strip()
                acc_num = input("Nhập số tài khoản 10 chữ số: ").strip()
                if not BaseAccount.validate_account_number(acc_num):
                    print("Số tài khoản không hợp lệ! Phải gồm đúng 10 chữ số.")
                    continue
                name = input("Nhập tên chủ tài khoản: ")
                
                match type_choice:
                    case "1":
                        rate_input = input("Nhập lãi suất năm (ví dụ 0.06): ").strip()
                        bal_input = input("Nhập số dư ban đầu: ").strip()
                        rate = float(rate_input) if rate_input.replace('.', '', 1).isdigit() else 0.06
                        balance = float(bal_input) if bal_input.replace('.', '', 1).isdigit() else 0.0
                        new_acc = SavingsAccount(acc_num, name, rate, balance)
                        print(f"Mở tài khoản Tiết kiệm thành công! Chủ tài khoản: {new_acc.account_holder}")
                    case "2":
                        limit_input = input("Nhập hạn mức tín dụng (ví dụ 20000000): ").strip()
                        bal_input = input("Nhập số dư ban đầu (thường là 0): ").strip()
                        limit = float(limit_input) if limit_input.replace('.', '', 1).isdigit() else 20000000.0
                        balance = float(bal_input) if bal_input.replace('.', '', 1).isdigit() else 0.0
                        new_acc = CreditAccount(acc_num, name, limit, balance)
                        print(f"Mở tài khoản Tín dụng thành công! Chủ tài khoản: {new_acc.account_holder}")
                    case "3":
                        rate_input = input("Nhập lãi suất năm cho phần tích lũy (ví dụ 0.06): ").strip()
                        bal_input = input("Nhập số dư ban đầu: ").strip()
                        rate = float(rate_input) if rate_input.replace('.', '', 1).isdigit() else 0.06
                        balance = float(bal_input) if bal_input.replace('.', '', 1).isdigit() else 0.0
                        new_acc = HybridAccount(acc_num, name, rate, balance)
                        print(f"Mở tài khoản Đa năng Hybrid thành công! Chủ tài khoản: {new_acc.account_holder}")
                    case _:
                        print("Lựa chọn loại tài khoản không hợp lệ.")
                        continue
                accounts.append(new_acc)
                current_account = new_acc
            case "2":
                if not current_account:
                    print("Hệ thống chưa có thông tin tài khoản. Vui lòng mở tài khoản ở Chức năng 1 trước.")
                    continue
                print("--- THÔNG TIN TÀI KHOẢN HIỆN TẠI ---")
                print(f"Loại tài khoản: {type(current_account).__name__}")
                print(f"Ngân hàng: {current_account.bank_name}")
                print(f"Số tài khoản: {current_account.account_number}")
                print(f"Chủ tài khoản: {current_account.account_holder}")
                print(f"Số dư: {current_account.balance:,.0f} VND")
                if hasattr(current_account, "interest_rate"):
                    print(f"Lãi suất: {current_account.interest_rate * 100}% / năm")
                if hasattr(current_account, "credit_limit"):
                    print(f"Hạn mức tín dụng: {current_account.credit_limit:,.0f} VND")
                print("[Kiểm tra kỹ thuật MRO của Lớp này]:")
                mro_list = [cls.__name__ for cls in type(current_account).__mro__]
                print(" -> ".join(mro_list))
            case "3":
                if not current_account:
                    print("Hệ thống chưa có thông tin tài khoản. Vui lòng mở tài khoản ở Chức năng 1 trước.")
                    continue
                print("--- GIAO DỊCH NẠP / RÚT TIỀN ---")
                print("1. Nạp tiền")
                print("2. Rút tiền")
                tx_choice = input("Chọn giao dịch (1-2): ").strip()
                amount_input = input("Nhập số tiền giao dịch: ").strip()
                if amount_input.replace('.', '', 1).isdigit():
                    amount = float(amount_input)
                    match tx_choice:
                        case "1":
                            if current_account.deposit(amount):
                                print(f"Số dư hiện tại: {current_account.balance:,.0f} VND")
                        case "2":
                            if current_account.withdraw(amount):
                                print(f"Số dư còn lại: {current_account.balance:,.0f} VND")
                        case _:
                            print("Lựa chọn không hợp lệ.")
                else:
                    print("Số tiền nhập vào không hợp lệ.")
            case "4":
                if not current_account:
                    print("Hệ thống chưa có thông tin tài khoản. Vui lòng mở tài khoản ở Chức năng 1 trước.")
                    continue
                print("--- TÍNH LÃI ĐỊNH KỲ ---")
                if hasattr(current_account, "apply_interest"):
                    old_bal, interest, new_bal = current_account.apply_interest()
                    print(f"Số dư trước tính lãi: {old_bal:,.0f} VND")
                    print(f"Lãi suất năm: {current_account.interest_rate * 100}%")
                    print(f"Tiền lãi nhận được: +{interest:,.0f} VND")
                    print(f"Số dư mới sau khi cộng lãi: {new_bal:,.0f} VND")
                else:
                    print("Tính năng không hỗ trợ! Tài khoản hiện tại không có chức năng tích lũy sinh lãi.")
            case "5":
                if not current_account:
                    print("Hệ thống chưa có thông tin tài khoản. Vui lòng mở tài khoản ở Chức năng 1 trước.")
                    continue
                print("--- ĐỒNG BỘ & SO SÁNH TÀI KHOẢN (OPERATOR OVERLOADING) ---")
                counterparty_accounts = [acc for acc in accounts if acc.account_number != current_account.account_number]
                if not counterparty_accounts:
                    print("Hệ thống hiện tại không có tài khoản thứ hai để đối ứng.")
                    continue
                print(f"Tài khoản hiện tại (A): {current_account.account_holder} (Số dư: {current_account.balance:,.0f} VND)")
                print("Danh sách tài khoản đối ứng trong hệ thống:")
                for idx, acc in enumerate(counterparty_accounts):
                    print(f"[{idx}] Số TK: {acc.account_number} - Chủ TK: {acc.account_holder} - Số dư: {acc.balance:,.0f} VND")
                idx_choice_input = input("Chọn tài khoản đối ứng (B) theo số thứ tự: ").strip()
                if idx_choice_input.isdigit() and int(idx_choice_input) < len(counterparty_accounts):
                    account_b = counterparty_accounts[int(idx_choice_input)]
                    if current_account < account_b:
                        print("[Kết quả So sánh (__lt__)]: Số dư tài khoản A NHỎ HƠN số dư tài khoản B.")
                    else:
                        print("[Kết quả So sánh (__lt__)]: Số dư tài khoản A LỚN HƠN HOẶC BẰNG số dư tài khoản B.")
                    total_money = current_account + account_b
                    if isinstance(total_money, float) or isinstance(total_money, int):
                        print(f"[Kết quả Tổng hợp (__add__)]: Tổng số tiền sở hữu của cả 2 tài khoản là: {total_money:,.0f} VND.")
                    else:
                        print(total_money)
                else:
                    print("Lựa chọn tài khoản đối ứng không hợp lệ.")
            case "6":
                if not current_account:
                    print("Hệ thống chưa có thông tin tài khoản. Vui lòng mở tài khoản ở Chức năng 1 trước.")
                    continue
                print("--- THANH TOÁN HÓA ĐƠN QUA CỔNG TRUNG GIAN ---")
                print("1. Thanh toán qua VNPay")
                print("2. Thanh toán qua Viettel Money")
                gateway_choice = input("Chọn cổng thanh toán (1-2): ").strip()
                
                match gateway_choice:
                    case "1":
                        gateway = VNPayGateway()
                    case "2":
                        gateway = ViettelMoneyGateway()
                    case _:
                        print("Cổng thanh toán không xác định.")
                        continue
                
                bill_input = input("Nhập số tiền hóa đơn: ").strip()
                if bill_input.replace('.', '', 1).isdigit():
                    bill_amount = float(bill_input)
                    success = process_payment(gateway, current_account, bill_amount)
                    if success:
                        print("Xác thực thanh toán bằng Duck Typing thành công!")
                        print(f"Tài khoản đã thanh toán hóa đơn giá trị: {bill_amount:,.0f} VND.")
                        print(f"Số dư mới: {current_account.balance:,.0f} VND.")
                    else:
                        print("Giao dịch thanh toán qua cổng trung gian thất bại.")
                else:
                    print("Số tiền không hợp lệ.")
            case "7":
                print("Cảm ơn đã trải nghiệm hệ thống Vietcombank Digibank Pro Simulator!")
                break
            case _:
                print("Lựa chọn không hợp lệ, vui lòng nhập từ 1 đến 7.")

if __name__ == "__main__":
    main()


# Kiến trúc tài khoản: Hệ thống sử dụng mô hình kế thừa từ lớp cơ sở trừu tượng (BaseAccount) 
# kết hợp lớp bổ trợ độc lập (Mixin) để tối ưu tái 
# sử dụng mã nguồn và tạo ra tài khoản tích hợp (HybridAccount)

# Cơ chế MRO (C3 Linearization): Quy định thứ tự tìm kiếm phương thức từ trái qua phải, từ dưới 
# lên trên nhằm giải quyết xung đột "bài toán Kim cương" trong đa kế thừa khi gọi super()

# Cơ chế Duck Typing: Cho phép hệ thống tích hợp vô số cổng thanh toán mới mà không cần sửa đổi mã nguồn cốt lõi, 
# chỉ cần đối tượng truyền vào sở hữu đúng tên phương thức yêu cầu (execute_pay).