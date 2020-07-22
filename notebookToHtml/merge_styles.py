# ============================================ Importing packages ======================================================
import bs4 as htmlLib
import re


def merge_styles(filepath):
    # ======================================= Create a BeautifulSoup Object ============================================
    with open(filepath, "r", encoding="utf8") as fp:
        html_soup = htmlLib.BeautifulSoup(fp, "html.parser", from_encoding='utf-8')

    # ========================================= Find all style tags ====================================================
    for s in html_soup.select('style'):
        # Extract them from html file
        s.extract()

    # ========================================= Find all link tags =====================================================
    for s in html_soup.select('link'):
        if "custom.css" in s.attrs["href"] or "theme_style.css" in s.attrs["href"]:
            # Extract them from html file
            s.extract()

    # ======================================= Create a new style tag ===================================================
    new_link = html_soup.new_tag('link')
    new_link.attrs["href"] = "../../styles/bsnb_style.css"
    new_link.attrs["rel"] = "stylesheet"
    html_soup.html.head.append(new_link)

    # ===================================== Add Google Analytics Script ================================================
    #new_script = html_soup.new_tag('script')
    #new_script.attrs["async"] = None
    #new_script.attrs["src"] = "https://www.googletagmanager.com/gtag/js?id=UA-38036509-7"
    #html_soup.html.head.append(new_script)

    # ========================================= Remove empty lines =====================================================
    head_obj = html_soup.find("head")
    pattern = re.compile("^\n$")
    prev_item = None
    for item_nbr, item in enumerate(head_obj):
        if isinstance(item, htmlLib.NavigableString) and isinstance(prev_item, htmlLib.NavigableString) and pattern.match(
                prev_item):
            if pattern.match(item.string):
                item.replace_with("")
        # Prepare next iteration
        prev_item = item

    # ======================================= Store the unstyled result ================================================
    with open(filepath, "w", encoding="utf8") as fp:
        fp.write(str(html_soup))
