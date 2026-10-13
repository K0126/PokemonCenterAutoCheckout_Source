from PyQt5 import QtCore
import json
import time
import os
import random
import subprocess
import requests
from playwright.sync_api import sync_playwright

class PokemonBuyer(QtCore.QThread):
    
    log_signal = QtCore.pyqtSignal(str)
    status_signal = QtCore.pyqtSignal(str, str)
    
    def __init__(self, product_url, profile_name, proxy, status_callback, log_callback):
        super().__init__()
        self.product_url = product_url
        self.profile_name = profile_name
        self.proxy = proxy
        self.status_callback = status_callback
        self.log_callback = log_callback
        self.is_running = True
        self.load_profile()
        
        self.log_signal.connect(self.log_callback)
        self.status_signal.connect(self.status_callback)
        
    def load_profile(self):
        try:
            with open(f"profiles/{self.profile_name}.json", "r", encoding='utf-8') as f:
                self.profile_data = json.load(f)
            self.log_signal.emit(f"✅ 프로필 '{self.profile_name}' 로드 완료")
        except Exception as e:
            self.log_signal.emit(f"⚠️ 프로필 로드 실패: {e}")
            self.profile_data = {
                "first_name": "John",
                "last_name": "Doe",
                "address": "123 Main St",
                "city": "Los Angeles",
                "state": "CA",
                "zip": "90001",
                "phone": "123-456-7890",
                "email": "guest@example.com",
                "card_number": "4111111111111111",
                "card_expiry": "07/2026",
                "card_cvv": "123"
            }
            os.makedirs("profiles", exist_ok=True)
            with open(f"profiles/{self.profile_name}.json", "w", encoding='utf-8') as f:
                json.dump(self.profile_data, f, indent=2)
            self.log_signal.emit(f"✅ 기본 프로필 생성 완료")
    
    def human_delay(self, min_sec=0.3, max_sec=0.8):
        time.sleep(random.uniform(min_sec, max_sec))
    
    def fill_field(self, page, selectors, value, field_name="field"):
        if not value:
            return False
        for selector in selectors:
            try:
                elem = page.locator(selector)
                if elem.count() > 0 and elem.first.is_visible():
                    elem.first.fill(value)
                    self.log_signal.emit(f"✅ {field_name} 입력 완료")
                    return True
            except:
                continue
        self.log_signal.emit(f"⚠️ {field_name} 필드를 찾을 수 없음")
        return False
    
    def fill_iframe_field(self, page, container_id, selectors, value, field_name="field", retries=15):
        """iframe 내부 필드 찾아 채우기 (수정 완료 - FrameLocator count 문제 해결)"""
        if not value:
            return False
        
        for attempt in range(retries):
            try:
                # 1. 컨테이너 div 확인
                container = page.locator(f"#{container_id}")
                if container.count() == 0:
                    self.log_signal.emit(f"⏳ {field_name} 컨테이너 찾는 중... ({attempt+1}/{retries})")
                    time.sleep(1)
                    continue
                
                # 2. iframe 찾기 (FrameLocator 생성)
                #    FrameLocator에는 count()가 없으므로, 내부 요소로 접근
                iframe = page.frame_locator(f"#{container_id} iframe")
                
                # 3. iframe 내부에서 입력 필드 찾기 (Locator로 변환)
                for selector in selectors:
                    try:
                        elem = iframe.locator(selector)
                        if elem.count() > 0 and elem.first.is_visible():
                            elem.first.fill(value)
                            self.log_signal.emit(f"✅ {field_name} 입력 완료 (iframe)")
                            return True
                    except Exception as e:
                        continue
                
                # 4. 대체 방법: src로 iframe 찾기
                try:
                    alt_iframe = page.frame_locator("iframe[src*='flex.cybersource.com']")
                    for selector in selectors:
                        try:
                            elem = alt_iframe.locator(selector)
                            if elem.count() > 0 and elem.first.is_visible():
                                elem.first.fill(value)
                                self.log_signal.emit(f"✅ {field_name} 입력 완료 (alt iframe)")
                                return True
                        except:
                            continue
                except:
                    pass
                
                self.log_signal.emit(f"⏳ {field_name} 입력 필드 찾는 중... ({attempt+1}/{retries})")
                time.sleep(1)
                
            except Exception as e:
                self.log_signal.emit(f"⚠️ {field_name} 시도 중 오류: {e}")
                time.sleep(1)
        
        self.log_signal.emit(f"⚠️ {field_name} iframe 내부 필드를 찾을 수 없음 (재시도 실패)")
        return False
    
    def select_dropdown(self, page, selectors, value, field_name="dropdown"):
        for selector in selectors:
            try:
                elem = page.locator(selector)
                if elem.count() > 0 and elem.first.is_visible():
                    elem.first.select_option(value)
                    self.log_signal.emit(f"✅ {field_name} 선택 완료")
                    return True
            except:
                continue
        self.log_signal.emit(f"⚠️ {field_name} 드롭다운을 찾을 수 없음")
        return False
    
    def launch_chrome_debug(self):
        try:
            requests.get("http://localhost:9222/json/version", timeout=2)
            self.log_signal.emit("✅ 이미 실행 중인 크롬 디버그 발견")
            return True
        except:
            pass
        
        self.log_signal.emit("🚀 크롬을 디버그 모드로 실행 중...")
        
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe")
        ]
        chrome_path = None
        for path in chrome_paths:
            if os.path.exists(path):
                chrome_path = path
                break
        
        if not chrome_path:
            self.log_signal.emit("❌ 크롬 실행 파일을 찾을 수 없습니다.")
            return False
        
        user_data_dir = os.path.join(os.getcwd(), "chrome_profile")
        if not os.path.exists(user_data_dir):
            os.makedirs(user_data_dir)
        
        cmd = [
            chrome_path,
            f"--remote-debugging-port=9222",
            f"--user-data-dir={user_data_dir}",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-gpu",
            "--disable-dev-shm-usage",
            "--disable-blink-features=AutomationControlled",
            "--window-size=1920,1080",
            "--start-maximized"
        ]
        
        try:
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.log_signal.emit("⏳ 크롬 실행 중... (5초 대기)")
            time.sleep(5)
            try:
                requests.get("http://localhost:9222/json/version", timeout=2)
                self.log_signal.emit("✅ 크롬 디버그 모드 실행 완료")
                return True
            except:
                self.log_signal.emit("❌ 크롬 실행 실패 (포트 접근 불가)")
                return False
        except Exception as e:
            self.log_signal.emit(f"❌ 크롬 실행 오류: {e}")
            return False
    
    def run(self):
        self.log_signal.emit("🚀 포켓몬센터 구매 시작 (iframe 우회 최종)...")
        self.log_signal.emit(f"🔗 상품: {self.product_url}")
        self.log_signal.emit(f"👤 프로필: {self.profile_name}")
        
        if not self.launch_chrome_debug():
            self.log_signal.emit("❌ 크롬 디버그 실행 실패.")
            self.status_signal.emit("실패", "#FF4444")
            return
        
        try:
            with sync_playwright() as p:
                self.log_signal.emit("🌐 진짜 크롬에 연결 중...")
                browser = p.chromium.connect_over_cdp("http://localhost:9222")
                
                if browser.contexts:
                    context = browser.contexts[0]
                else:
                    context = browser.new_context()
                
                if context.pages:
                    page = context.pages[0]
                else:
                    page = context.new_page()
                
                self.log_signal.emit("✅ 진짜 크롬 연결 성공!")
                
                # ============================================================
                # ===== 상품 페이지 =====
                # ============================================================
                self.log_signal.emit(f"🔗 상품 페이지로 이동 중...")
                page.goto(self.product_url, wait_until="networkidle", timeout=30000)
                self.human_delay(3, 5)
                
                # ============================================================
                # ===== 장바구니 버튼 =====
                # ============================================================
                self.log_signal.emit("🛒 장바구니 버튼 찾는 중...")
                add_btn = None
                add_selectors = [
                    "button:has-text('ADD TO CART')",
                    "button:has-text('Add to Cart')",
                    "button:has-text('add to cart')",
                    "button:has-text('장바구니')",
                    "button[data-testid='add-to-cart']",
                    ".add-to-cart-button",
                    "button.add-to-cart",
                ]
                
                for _ in range(10):
                    for selector in add_selectors:
                        try:
                            btn = page.locator(selector)
                            if btn.count() > 0 and btn.first.is_visible():
                                add_btn = btn
                                break
                        except:
                            continue
                    if add_btn:
                        break
                    time.sleep(1)
                
                if add_btn and add_btn.count() > 0:
                    add_btn.first.hover()
                    self.human_delay(0.3, 0.8)
                    add_btn.first.click()
                    self.log_signal.emit("✅ 장바구니 담기 성공!")
                    self.human_delay(2, 4)
                else:
                    self.log_signal.emit("❌ 장바구니 버튼 없음 (품절)")
                    self.status_signal.emit("품절", "#FF4444")
                    return
                
                # ============================================================
                # ===== 장바구니 페이지 =====
                # ============================================================
                self.log_signal.emit("🛒 장바구니 페이지 이동 중...")
                page.goto("https://www.pokemoncenter.com/cart", wait_until="networkidle")
                self.human_delay(2, 4)
                
                # ============================================================
                # ===== 체크아웃 =====
                # ============================================================
                self.log_signal.emit("💳 체크아웃 진행 중...")
                checkout_btn = page.locator("button:has-text('CHECKOUT')")
                if checkout_btn.count() > 0 and checkout_btn.first.is_visible():
                    checkout_btn.first.hover()
                    self.human_delay(0.3, 0.8)
                    checkout_btn.first.click()
                    self.log_signal.emit("✅ 체크아웃 이동 성공")
                    self.human_delay(3, 5)
                else:
                    self.log_signal.emit("❌ 체크아웃 버튼을 찾을 수 없음")
                    return
                
                # ============================================================
                # ===== 1. 배송 정보 입력 =====
                # ============================================================
                self.log_signal.emit("📝 배송 정보 입력 중...")
                
                # Given Name
                self.fill_field(
                    page,
                    [
                        "input[name='givenName']",
                        "input[id='shipping-givenName']",
                        "input[placeholder*='First']",
                        "input[aria-label='First Name']",
                        "input[data-testid='givenName']"
                    ],
                    self.profile_data.get("first_name", ""),
                    "Given Name (First Name)"
                )
                
                # Family Name
                self.fill_field(
                    page,
                    [
                        "input[name='familyName']",
                        "input[id='shipping-familyName']",
                        "input[placeholder*='Last']",
                        "input[aria-label='Last Name']",
                        "input[data-testid='familyName']"
                    ],
                    self.profile_data.get("last_name", ""),
                    "Family Name (Last Name)"
                )
                
                # Street Address
                self.fill_field(
                    page,
                    [
                        "input[name='address1']",
                        "input[name='streetAddress']",
                        "input[id='shipping-address1']",
                        "input[placeholder*='Street']",
                        "input[aria-label='Street Address']",
                        "input[data-testid='address']"
                    ],
                    self.profile_data.get("address", ""),
                    "Street Address"
                )
                
                # Zip Code
                self.fill_field(
                    page,
                    [
                        "input[name='postalCode']",
                        "input[name='zip']",
                        "input[id='shipping-postalCode']",
                        "input[placeholder*='Zip']",
                        "input[aria-label='Zip Code']",
                        "input[data-testid='zip']"
                    ],
                    self.profile_data.get("zip", ""),
                    "Zip Code"
                )
                
                # City
                self.fill_field(
                    page,
                    [
                        "input[name='city']",
                        "input[id='shipping-city']",
                        "input[placeholder*='City']",
                        "input[aria-label='City']",
                        "input[data-testid='city']"
                    ],
                    self.profile_data.get("city", ""),
                    "City"
                )
                
                # Phone
                self.fill_field(
                    page,
                    [
                        "input[name='phone']",
                        "input[name='phoneNumber']",
                        "input[id='shipping-phone']",
                        "input[placeholder*='Phone']",
                        "input[aria-label='Phone Number']",
                        "input[data-testid='phone']"
                    ],
                    self.profile_data.get("phone", ""),
                    "Phone Number"
                )
                
                # Email
                self.fill_field(
                    page,
                    [
                        "input[name='email']",
                        "input[id='shipping-email']",
                        "input[placeholder*='Email']",
                        "input[aria-label='Email']",
                        "input[data-testid='email']"
                    ],
                    self.profile_data.get("email", "guest@example.com"),
                    "Email"
                )
                
                # "Use as billing address"
                try:
                    checkbox = page.locator("input[type='checkbox'][name='useBilling']")
                    if checkbox.count() > 0 and checkbox.first.is_visible():
                        if not checkbox.first.is_checked():
                            checkbox.first.click()
                            self.log_signal.emit("✅ 'Use as billing address' 체크")
                except:
                    pass
                
                self.human_delay(1, 2)
                
                # ============================================================
                # ===== 2. CONTINUE 전 주소 포커스 =====
                # ============================================================
                self.log_signal.emit("🖱️ 주소 필드에 포커스 주는 중...")
                address_selectors = [
                    "input[name='address1']",
                    "input[name='streetAddress']",
                    "input[id='shipping-address1']",
                    "input[placeholder*='Street']",
                    "input[aria-label='Street Address']",
                    "input[data-testid='address']"
                ]
                focused = False
                for selector in address_selectors:
                    try:
                        elem = page.locator(selector)
                        if elem.count() > 0 and elem.first.is_visible():
                            elem.first.click()
                            self.log_signal.emit("✅ 주소 필드 포커스 완료")
                            focused = True
                            break
                    except:
                        continue
                
                if not focused:
                    try:
                        zip_elem = page.locator("input[name='postalCode']")
                        if zip_elem.count() > 0 and zip_elem.first.is_visible():
                            zip_elem.first.click()
                            self.log_signal.emit("✅ ZIP 필드 포커스 완료 (대체)")
                    except:
                        pass
                
                self.human_delay(0.5, 1.0)
                
                # ============================================================
                # ===== 3. CONTINUE 버튼 =====
                # ============================================================
                self.log_signal.emit("⏩ CONTINUE 버튼 클릭...")
                continue_btn = page.locator("button:has-text('CONTINUE')")
                if continue_btn.count() > 0 and continue_btn.first.is_visible():
                    continue_btn.first.hover()
                    self.human_delay(0.3, 0.6)
                    continue_btn.first.click()
                    self.log_signal.emit("✅ CONTINUE 클릭 완료")
                    self.human_delay(3, 5)
                else:
                    self.log_signal.emit("❌ CONTINUE 버튼을 찾을 수 없음")
                    return
                
                # ============================================================
                # ===== 4. 주소 확인 팝업 =====
                # ============================================================
                self.log_signal.emit("🔍 주소 확인 팝업 확인 중...")
                save_continue_btn = page.locator("button:has-text('Save and Continue')")
                if save_continue_btn.count() > 0 and save_continue_btn.first.is_visible():
                    self.log_signal.emit("✅ 주소 확인 팝업 발견")
                    save_continue_btn.first.hover()
                    self.human_delay(0.5, 1.0)
                    save_continue_btn.first.click()
                    self.log_signal.emit("✅ Save and Continue 클릭 완료")
                    self.human_delay(3, 5)
                else:
                    self.log_signal.emit("ℹ️ 주소 확인 팝업 없음 (건너뜀)")
                
                # ============================================================
                # ===== 5. 결제 수단 선택 =====
                # ============================================================
                self.log_signal.emit("💳 결제 수단 선택 중...")
                
                payment_selectors = [
                    "select#billing-selector",
                    "select.billing-method-selector--hoF5C",
                    "select[name='paymentMethod']",
                    "select[id='paymentMethod']",
                    "select[data-testid='paymentMethod']",
                    "select[aria-label='Payment Method']"
                ]
                
                payment_selected = False
                for selector in payment_selectors:
                    try:
                        elem = page.locator(selector)
                        if elem.count() > 0 and elem.first.is_visible():
                            elem.first.select_option(label="Credit/Debit Card")
                            self.log_signal.emit(f"✅ Credit/Debit Card 선택 완료 (select: {selector})")
                            payment_selected = True
                            break
                    except Exception as e:
                        continue
                
                if not payment_selected:
                    try:
                        dropdown_trigger = page.locator("[data-testid='payment-dropdown']")
                        if dropdown_trigger.count() == 0:
                            dropdown_trigger = page.locator("div[role='button']:has-text('Select payment method')")
                        if dropdown_trigger.count() == 0:
                            dropdown_trigger = page.locator("button:has-text('Select payment method')")
                        if dropdown_trigger.count() == 0:
                            dropdown_trigger = page.locator(".billing-method-selector--hoF5C")
                        
                        if dropdown_trigger.count() > 0 and dropdown_trigger.first.is_visible():
                            dropdown_trigger.first.click()
                            self.log_signal.emit("✅ 드롭다운 열림")
                            self.human_delay(0.5, 1.0)
                            
                            option = page.locator("li:has-text('Credit/Debit Card')")
                            if option.count() == 0:
                                option = page.locator("option:has-text('Credit/Debit Card')")
                            if option.count() == 0:
                                option = page.locator("[data-value='credit']")
                            if option.count() == 0:
                                option = page.locator("[data-value='Credit/Debit Card']")
                            
                            if option.count() > 0:
                                option.first.click()
                                self.log_signal.emit("✅ Credit/Debit Card 선택 완료 (custom)")
                                payment_selected = True
                    except Exception as e:
                        self.log_signal.emit(f"⚠️ 커스텀 드롭다운 오류: {e}")
                
                if not payment_selected:
                    self.log_signal.emit("❌ 결제 수단 드롭다운을 찾을 수 없음")
                
                self.human_delay(2, 4)
                
                # ============================================================
                # ===== 6. 카드 정보 입력 (iframe 내부 - FrameLocator 수정) =====
                # ============================================================
                self.log_signal.emit("💳 카드 정보 입력 중 (iframe)...")
                
                # Card Number
                card_found = self.fill_iframe_field(
                    page,
                    "card-number-container",
                    [
                        "input[name='number']",
                        "input#number",
                        "input[name='cardNumber']",
                        "input[id='cardNumber']",
                        "input[placeholder*='Card Number']",
                        "input[aria-label='Card number']",
                        "input[autocomplete='cc-number']"
                    ],
                    self.profile_data.get("card_number", ""),
                    "Card Number"
                )
                
                if not card_found:
                    self.log_signal.emit("⚠️ Card Number 필드를 찾을 수 없음")
                
                # CVV2
                cvv_found = self.fill_iframe_field(
                    page,
                    "security-code-container",
                    [
                        "input[name='securityCode']",
                        "input#securityCode",
                        "input[name='cvv']",
                        "input[name='cvc']",
                        "input[id='cvv']",
                        "input[placeholder*='CVV']",
                        "input[aria-label='Card security code']",
                        "input[autocomplete='cc-csc']"
                    ],
                    self.profile_data.get("card_cvv", ""),
                    "CVV2"
                )
                
                if not cvv_found:
                    self.log_signal.emit("⚠️ CVV2 필드를 찾을 수 없음")
                
                # Expiry Month & Year
                expiry_raw = self.profile_data.get("card_expiry", "07/2026")
                if "/" in expiry_raw:
                    month, year = expiry_raw.split("/")
                else:
                    parts = expiry_raw.split("/")
                    month = parts[0]
                    year = "20" + parts[1] if len(parts[1]) == 2 else parts[1]
                
                month = month.strip()
                year = year.strip()
                
                self.select_dropdown(
                    page,
                    [
                        "select#expiryMonth",
                        "select[name='expiryMonth']",
                        "select[id='expiryMonth']",
                        "select[aria-label='Month']",
                        "select[data-testid='expiryMonth']"
                    ],
                    month,
                    "Expiry Month"
                )
                
                self.select_dropdown(
                    page,
                    [
                        "select#expiryYear",
                        "select[name='expiryYear']",
                        "select[id='expiryYear']",
                        "select[aria-label='Year']",
                        "select[data-testid='expiryYear']"
                    ],
                    year,
                    "Expiry Year"
                )
                
                self.human_delay(2, 4)
                
                # ============================================================
                # ===== 7. CONTINUE 버튼 (결제) =====
                # ============================================================
                self.log_signal.emit("⏩ CONTINUE 버튼 클릭 (결제)...")
                continue_payment_btn = page.locator("button:has-text('CONTINUE')")
                if continue_payment_btn.count() > 0 and continue_payment_btn.first.is_visible():
                    continue_payment_btn.first.hover()
                    self.human_delay(0.3, 0.6)
                    continue_payment_btn.first.click()
                    self.log_signal.emit("✅ CONTINUE (결제) 클릭 완료")
                    self.human_delay(3, 5)
                else:
                    self.log_signal.emit("❌ CONTINUE (결제) 버튼을 찾을 수 없음")
                    return
                
                # ============================================================
                # ===== 8. 최종 주문 =====
                # ============================================================
                self.log_signal.emit("🎯 최종 주문 버튼 클릭...")
                order_btn = page.locator("button:has-text('PLACE ORDER')")
                if order_btn.count() > 0 and order_btn.first.is_visible():
                    order_btn.first.hover()
                    self.human_delay(0.5, 1.0)
                    order_btn.first.click()
                    self.log_signal.emit("🎉🎉🎉 주문 완료!!!")
                    self.status_signal.emit("주문 완료", "#4CAF50")
                    
                    screenshot_dir = "screenshots"
                    os.makedirs(screenshot_dir, exist_ok=True)
                    filename = f"{screenshot_dir}/order_{int(time.time())}.png"
                    page.screenshot(path=filename)
                    self.log_signal.emit(f"📸 스크린샷 저장됨: {filename}")
                else:
                    self.log_signal.emit("❌ PLACE ORDER 버튼을 찾을 수 없음")
                    self.log_signal.emit("💡 수동으로 주문을 완료해주세요")
                    self.status_signal.emit("수동 필요", "#FFA500")
                
                self.human_delay(3, 5)
                self.log_signal.emit("✅ 브라우저 연결 종료")
                
        except Exception as e:
            self.log_signal.emit(f"❗ 치명적 오류: {e}")
            self.status_signal.emit("오류", "#FF4444")

    def stop(self):
        self.is_running = False
        self.terminate()
        self.wait()