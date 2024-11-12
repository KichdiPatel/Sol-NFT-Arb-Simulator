# Iterate Magic Eden popular listings
# Open each magic eden collection. Record offer price and floor price
# Reload tensor each iteration and check the floor and "sell now " prices
# Compare prices to see if there is an arb in either direction
#
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import time

# This is a dictionary containing some of the popular NFT collections direct links on magic eden and tensor
# This way I don't have to scrape coingecko everytime
LINKS = {
    "Froganas": {
        "ME": "https://magiceden.io/marketplace/froganas",
        "Tensor": "https://www.tensor.trade/trade/froganas",
    },
    "Mad Lads": {
        "ME": "https://magiceden.io/marketplace/mad_lads",
        "Tensor": "https://www.tensor.trade/trade/madlads",
    },
    "Famous Fox Federation": {
        "ME": "https://magiceden.io/marketplace/famous_fox_federation",
        "Tensor": "https://www.tensor.trade/trade/famous_fox_federation",
    },
    "cryptoundeads": {
        "ME": "https://magiceden.io/marketplace/cryptoundeads",
        "Tensor": "https://www.tensor.trade/trade/cryptoundeads",
    },
    "BoDoggos": {
        "ME": "https://magiceden.io/marketplace/bodoggos",
        "Tensor": "https://www.tensor.trade/trade/bodoggos",
    },
    "Claynosaurz": {
        "ME": "https://magiceden.io/marketplace/claynosaurz",
        "Tensor": "https://www.tensor.trade/trade/claynosaurz",
    },
    "sharx by sharky.fi": {
        "ME": "https://magiceden.io/marketplace/sharx",
        "Tensor": "https://www.tensor.trade/trade/sharx",
    },
    "Okay Bears": {
        "ME": "https://magiceden.io/marketplace/okay_bears",
        "Tensor": "https://www.tensor.trade/trade/okay_bears",
    },
    "AssetDash Vanta": {
        "ME": "https://magiceden.io/marketplace/assetdash_vanta",
        "Tensor": "https://www.tensor.trade/trade/assetdash_vanta",
    },
    "Solana Monkey Business": {
        "ME": "https://magiceden.io/marketplace/solana_monkey_business",
        "Tensor": "https://www.tensor.trade/trade/solana_monkey_business",
    },
}


# This is a way to get the tensor and magic eden links of a nft collection from a coingecko page
def scrapeGeckoPage(ext):
    url = "https://www.coingecko.com" + ext
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(url)
        page.wait_for_timeout(500)

        html = page.inner_html(".table-responsive")
        browser.close()

    s = BeautifulSoup(html, "html.parser")
    a_tags = s.find_all("a", target="_blank")
    href_values = [a.get("href") for a in a_tags]

    vals = {"ME": "", "Tensor": ""}

    for link in href_values:
        if "tensor" in link:
            vals["Tensor"] = link
        elif "magiceden" in link:
            vals["ME"] = link

    return vals


# This scrapes the top popular NFT collections on Solana
def scrapeCoinGecko():
    url = "https://www.coingecko.com/en/nft/solana"
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(url)
        page.wait_for_timeout(1500)

        html = page.inner_html(".gecko-table-container")
        soup = BeautifulSoup(html, "html.parser")

        td_with_href = soup.find_all("td", {"class": None})

        # Extract href values
        href_values = [td.find("a").get("href") for td in td_with_href if td.find("a")]

        return href_values


# This scrapes the ask and bid prices from tensor on a given collection.
# I refer to them as buy_now and sell_now
def tensorPrices(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(url)
        page.wait_for_timeout(2000)

        # Getting the prices
        html = page.inner_html(".css-1tb027r")
        browser.close()

    s = BeautifulSoup(html, "html.parser")
    buy_now = s.find("b", class_="chakra-text css-1gl96jh").text
    sell_now = s.find("b", class_="chakra-text css-l3z3xi").text

    return (float(buy_now), float(sell_now))


# This scrapes the ask and bid prices from magic eden on a given collection.
# I refer to them as buy_now and sell_now
def magicEdenPrices(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(url)
        page.wait_for_timeout(10000)

        # Getting the prices
        html = page.inner_html("#collectionInfoTip")
        # print(html)
        browser.close()

    s = BeautifulSoup(html, "html.parser")
    floor_price_container = s.find("span", {"data-test-id": "floor price"})
    buy_now = floor_price_container.find("span", class_="tw-text-white-2").text

    top_offer_container = s.find("span", {"data-test-id": "top offer"})
    sell_now = top_offer_container.find("span", class_="tw-text-white-2").text

    return (float(buy_now), float(sell_now))


# WRAPPERS for tensorPrices and magicEdenPrices


def tensor(url):
    if url == "https://www.tensor.trade/trade/":
        print("Bad link. Moving on...")
        return False

    for attempt in range(2):
        try:
            tensor_prices = tensorPrices(url)
            return tensor_prices
        except:
            print(f"Failed finding tensor price: {url}")

    print("Couldn't get tensor prices. Moving on...")
    return False


def me(url):
    if url == "https://www.tensor.trade/trade/":
        print("Bad link. Moving on...")
        return False

    for attempt in range(2):
        try:
            me_prices = magicEdenPrices(url)
            return me_prices
        except:
            print(f"Failed finding me price: {url}")

    print("Couldn't get magic eden prices. Moving on...")
    return False


# Given tensor and magic eden ask and bid prices, this calculates if there is a arbitrage opportunity
def findArb(tensorPrice, magicedenPrice, collectionName):
    if tensorPrice != False and magicedenPrice != False:
        if tensorPrice == False:
            me_buy = magicedenPrice[0]
            me_sell = magicedenPrice[1]

            me_arb = me_sell - me_buy
            tensor_arb = -10000000000000000000000000
            arbs = [me_arb, tensor_arb]

        elif magicedenPrice == False:
            tensor_buy = tensorPrice[0]
            tensor_sell = tensorPrice[1]

            tensor_arb = tensor_sell - tensor_buy
            me_arb = -10000000000000000000000000
            arbs = [me_arb, tensor_arb]

        else:
            me_buy = magicedenPrice[0]
            me_sell = magicedenPrice[1]
            tensor_buy = tensorPrice[0]
            tensor_sell = tensorPrice[1]

            me_arb = me_sell - me_buy
            tensor_arb = tensor_sell - tensor_buy

            me_to_tensor_arb = tensor_sell - me_buy
            tensor_to_me_arb = me_sell - tensor_buy

            arbs = [me_arb, tensor_arb, me_to_tensor_arb, tensor_to_me_arb]

        arb_op = sorted(arbs, reverse=True)[0]

        if arb_op <= 0:
            print(f"{collectionName}: No Arb available")
            return 0
        else:
            if arb_op == me_arb:
                print(
                    f"{collectionName}: Buy on ME for {me_buy}. Sell on ME for {me_sell}. Profit = {me_arb}"
                )
                return me_arb

            elif arb_op == tensor_arb:
                print(
                    f"{collectionName}: Buy on Tensor for {tensor_buy}. Sell on Tensor for {tensor_sell}. Profit = {tensor_arb}"
                )
                return tensor_arb

            elif arb_op == me_to_tensor_arb:
                print(
                    f"{collectionName}: Buy on ME for {me_buy}. Sell on Tensor for {tensor_sell}. Profit = {me_to_tensor_arb}"
                )
                return me_to_tensor_arb

            elif arb_op == tensor_to_me_arb:
                print(
                    f"{collectionName}: Buy on Tensor for {tensor_buy}. Sell on ME for {me_sell}. Profit = {tensor_to_me_arb}"
                )
                return tensor_to_me_arb
    else:
        return 0


# This is a wrapper to iterate through each collction and determine if there is an arb opportunity on that collection
def iterateCollections():
    # hrefs = links  # scrapeCoinGecko()[:15]
    profit = 0

    for collection_name, marketplaces in LINKS.items():
        if marketplaces["ME"] != "" and marketplaces["Tensor"] != "":
            tensor_prices = tensor(marketplaces["Tensor"])
            me_prices = me(marketplaces["ME"])
            profit += findArb(tensor_prices, me_prices, collection_name)

    return profit


# Using the pushover api, this method uses the pushover api to send a message of the total profit calculated once this program is done checking all the
# listings
def alert(msg):
    import http.client, urllib

    conn = http.client.HTTPSConnection("api.pushover.net:443")
    conn.request(
        "POST",
        "/1/messages.json",
        urllib.parse.urlencode(
            {
                "token": "token",
                "user": "user",
                "message": msg,
            }
        ),
        {"Content-type": "application/x-www-form-urlencoded"},
    )
    conn.getresponse()


# This simply looks through everything searching for an opportunity and alerts if there was any opportunities
def runCheck():
    arb_op = iterateCollections()

    if arb_op > 0:
        alert(f"Total Profit = {arb_op}")


if __name__ == "__main__":
    while True:
        runCheck()
        time.sleep(900)
