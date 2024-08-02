import asyncio, winreg
from mitmproxy import options, http
from mitmproxy.tools import dump
from rich.console import Console
from bs4 import BeautifulSoup

console = Console(width=100)
console.print(f"[bold dark_orange]THT ELEMENT INJECTION (EĞİTİM AMAÇLIDIR / FOR EDUCATION)[/bold dark_orange]", no_wrap=True)

# SECTION Kodun çalışması için genel ayarlar.
LISTEN_HOST = "127.0.0.1"
LISTEN_PORT = 1881
NET_DUMP_LOG = False
START_PROXY_WHEN_OPENING = True
# !SECTION

# SECTION Proxy ayarlarını bu iki fonksiyon yapılandırır.
def set_proxy_settings():
    try:
        registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                      r"Software\Microsoft\Windows\CurrentVersion\Internet Settings", 0,
                                      winreg.KEY_WRITE)
        winreg.SetValueEx(registry_key, "ProxyEnable", 0, winreg.REG_DWORD, 1)
        winreg.SetValueEx(registry_key, "ProxyServer", 0, winreg.REG_SZ,
                          f"{LISTEN_HOST}:{str(LISTEN_PORT)}")
        winreg.FlushKey(registry_key)
        winreg.CloseKey(registry_key)
    except Exception as e:
        print("Proxy ayarlarını güncellemede bir hata oluştu:", e)

def disable_proxy_settings():
    try:
        registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                      r"Software\Microsoft\Windows\CurrentVersion\Internet Settings", 0,
                                      winreg.KEY_WRITE)
        winreg.SetValueEx(registry_key, "ProxyEnable", 0, winreg.REG_DWORD, 0)
        winreg.FlushKey(registry_key)
        winreg.CloseKey(registry_key)
    except Exception as e:
        print("Proxy ayarları kaldırılırken bir hata meydana geldi:", e)
# !SECTION

# SECTION HTML kodları aralalığı almak için method.
def parse_html(text, start, end):
    try:
        return text.split(start)[1].split(end)[0]
    except:
        return None
# !SECTION

# SECTION Yazılım açıldığında otomatik olarak sistem proxysini ayarlar.
# NOTE İsteğe bağlı genel ayarlardan kapatılabilir.
if START_PROXY_WHEN_OPENING:
    set_proxy_settings()
# !SECTION

# SECTION Yazılım ana kod parçacığı.
class RequestLogger:
    async def response(self, flow: http.HTTPFlow):
        if str(flow.request.url).startswith("https://sandbox.oniyevski.com/element-injection"): # Değişim yapacağım sayfaya girdiğinde bağlantıyı yakalıyoruz.
            original_content = flow.response.get_text()
            soup = BeautifulSoup(original_content, 'html.parser')
            # NOTE Alt satırda https://sandbox.oniyevski.com/element-injection sayfasında bütün kartları aratıyoruz ve biz reklam 2'yi düzenlemek 
            # istediğimiz için ve reklam 2 sonucu kart olduğu için -1 ile çekiyoruz. Eğer biz Reklam 1'i seçmek istesek -2 alabilirdik.
            get_ad_2 = soup.find_all("div", attrs={"class": "card mb-4 shadow-sm"})[-1]
            # NOTE Şimdi <h5 class="card-title"></h5> gibi başlıkların arasını düzenlemeyi görelim.
            orginal = str(get_ad_2)
            # NOTE Yukarıdaki satırla orjinal elementin bir örneğini tutuyoruz.
            get_ad_2 = str(get_ad_2)
            # NOTE Reklam 2 başlığını değiştirelim.
            get_ad_2 = get_ad_2.replace(
                parse_html(
                    get_ad_2,
                    '<h5 class="card-title">',
                    '</h5>'
                ),
                "Türk Hack Team"
            )
            # NOTE Reklam açıklamasını değiştirelim.
            get_ad_2 = get_ad_2.replace(
                parse_html(
                    get_ad_2,
                    '<p class="card-text">',
                    '</p>'
                ),
                "TurkHackTeam ya da kısa adıyla THT, 2002 yılında Arsenik tarafından kurulmuş, Türkiye'nin en eski siber güvenlik ve hacking forumlarından biridir."
            )
            # NOTE Daha fazla bilgiye basınca foruma gidecek şekilde ayarlayalım.
            get_ad_2 = get_ad_2.replace(
                parse_html(
                    get_ad_2,
                    '<a class="btn btn-primary" href="',
                    '">Daha Fazla Bilgi</a>'
                ),
                "https://turkhackteam.org/"
            )
            # NOTE Reklam görselini değiştirelim.
            get_ad_2 = get_ad_2.replace(
                parse_html(
                    get_ad_2,
                    'class="card-img-top" src="',
                    '"/>'
                ),
                "https://www.turkhackteam.org/styles/v1/tht/logo.png"
            )
            # Aşağıdaki örneklerle oynarken seçtiğiniz haricindekileri yorum satırına almayı unutmayın.
            # NOTE ÖRNEK 1 (Direkt olarak reklamı değiştirme): Alttaki 3 satırla birlikte orjinal veri üzerinden modifiyeli veriyi cevapta manipüle ediyoruz.
            soup = str(soup)
            soup = soup.replace(orginal, orginal + get_ad_2)
            flow.response.set_text(soup)
            # NOTE ÖRNEK 2 (Direkt olarak reklamı değiştirme): Alttaki 3 satırla birlikte orjinal veri üzerindeki reklamı modifiyeli veriyle cevapta manipüle ediyoruz.
            #soup = str(soup)
            #soup = soup.replace(orginal, get_ad_2)
            #flow.response.set_text(soup)
            # NOTE ÖRNEK 3 (Aynı reklamı çoğaltma): Alttaki 3 satırla birlikte orjinal veri üzerinden reklamı 2 adet modifiyeli veriyle  cevapta manipüle ediyoruz.
            #soup = str(soup)
            #soup = soup.replace(orginal, get_ad_2 + get_ad_2)
            #flow.response.set_text(soup)
            
# !SECTION

# SECTION Yazılımın asenkron çalışması için gereken kısımlar.
async def start_proxy(host, port):
    opts = options.Options(listen_host=host, listen_port=port)
    master = dump.DumpMaster(
        opts,
        with_termlog=NET_DUMP_LOG,
        with_dumper=NET_DUMP_LOG,
    )
    master.addons.add(RequestLogger())
    await master.run()
    return master

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

async def create_tasks_func(host, port):
    tasks = []
    tasks.append(asyncio.create_task(start_proxy(host, port)))
    await asyncio.wait(tasks)

def main():
    try:
        loop.run_until_complete(create_tasks_func(LISTEN_HOST, LISTEN_PORT)) 
        loop.close()
    except Exception as e:
        print(e)

if __name__ == '__main__':
    main()
# !SECTION