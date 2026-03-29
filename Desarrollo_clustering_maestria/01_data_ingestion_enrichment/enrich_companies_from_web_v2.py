import pandas as pd
import requests
import time
import re
from bs4 import BeautifulSoup
from urllib.parse import quote, urlparse

INPUT_FILE = r"E:\TESIS MAESTRIA\Desarrollo_clustering_maestria\01_data_ingestion_enrichment\leads.xlsx"      # o leads.csv
OUTPUT_FILE = "leads_enriquecidos.xlsx"
SHEET_NAME = 0                 # cambia si quieres una hoja específica
COMPANY_COL = "Company"
DELAY_SECONDS = 2

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36"
}

def load_file(path, sheet_name=0):
    if path.lower().endswith(".csv"):
        return pd.read_csv(path)
    return pd.read_excel(path, sheet_name=sheet_name)

def clean_company_name(name):
    if pd.isna(name):
        return None
    name = str(name).strip()
    if not name:
        return None
    return re.sub(r"\s+", " ", name)

def duckduckgo_html_search(query, max_results=5):
    """
    Busca resultados en DuckDuckGo HTML.
    Devuelve una lista de dicts con title, url y snippet.
    """
    url = "https://html.duckduckgo.com/html/"
    params = {"q": query}
    resp = requests.post(url, data=params, headers=HEADERS, timeout=25)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "lxml")
    results = []

    for result in soup.select(".result"):
        a = result.select_one(".result__title a")
        snippet = result.select_one(".result__snippet")
        if a:
            title = a.get_text(" ", strip=True)
            href = a.get("href", "")
            text = snippet.get_text(" ", strip=True) if snippet else ""
            results.append({
                "title": title,
                "url": href,
                "snippet": text
            })
        if len(results) >= max_results:
            break

    return results

def extract_domain(url):
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        domain = domain.replace("www.", "")
        return domain
    except:
        return None

def is_linkedin_company(url):
    return "linkedin.com/company/" in url.lower()

def looks_like_official_website(company, url, title):
    """
    Heurística simple para detectar web oficial.
    """
    bad_domains = [
        "linkedin.com", "facebook.com", "instagram.com", "twitter.com",
        "x.com", "youtube.com", "crunchbase.com", "bloomberg.com",
        "zoominfo.com", "glassdoor.com", "wikipedia.org"
    ]
    domain = extract_domain(url)
    if not domain:
        return False

    if any(bad in domain for bad in bad_domains):
        return False

    company_tokens = re.findall(r"[a-z0-9]+", company.lower())
    joined = " ".join(company_tokens)

    text = f"{title} {domain}".lower()
    score = sum(1 for token in company_tokens if token in text)

    return score >= 1 or joined.replace(" ", "") in text.replace(".", "").replace("-", "")

def fetch_page_metadata(url):
    """
    Intenta leer título y descripción de la web oficial.
    """
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20, allow_redirects=True)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")

        title = soup.title.get_text(" ", strip=True) if soup.title else None

        description = None
        meta_desc = soup.find("meta", attrs={"name": re.compile("^description$", re.I)})
        if meta_desc:
            description = meta_desc.get("content")

        return {
            "final_url": resp.url,
            "title": title,
            "description": description
        }
    except:
        return {
            "final_url": url,
            "title": None,
            "description": None
        }

def guess_country(text):
    if not text:
        return None

    countries = [
        "ecuador", "colombia", "peru", "chile", "mexico", "argentina",
        "spain", "españa", "united states", "usa", "canada", "brazil",
        "brasil", "panama", "panamá", "costa rica", "guatemala",
        "dominican republic", "republica dominicana", "uruguay", "paraguay",
        "bolivia", "venezuela"
    ]

    low = text.lower()
    for c in countries:
        if c in low:
            return c.title()

    return None

def guess_industry(text):
    if not text:
        return None

    industry_keywords = {
        "Financial Services": ["financial", "bank", "banking", "fintech", "insurance", "wealth"],
        "Technology": ["software", "saas", "technology", "it services", "cloud", "data", "analytics"],
        "Healthcare": ["health", "hospital", "medical", "pharma", "clinic"],
        "Retail": ["retail", "ecommerce", "store", "consumer"],
        "Manufacturing": ["manufacturing", "industrial", "factory", "production"],
        "Education": ["education", "university", "school", "learning"],
        "Consulting": ["consulting", "advisory", "professional services"],
        "Telecommunications": ["telecom", "telecommunications", "connectivity"],
        "Logistics": ["logistics", "transport", "shipping", "supply chain"],
        "Energy": ["energy", "oil", "gas", "utilities", "renewable"]
    }

    low = text.lower()
    for industry, words in industry_keywords.items():
        if any(w in low for w in words):
            return industry

    return None

def find_company_info(company):
    result = {
        "Company": company,
        "Website_found": None,
        "Linkedin_found": None,
        "Industry_found": None,
        "Country_found": None,
        "Website_title": None,
        "Website_description": None,
        "Status": "NOT_FOUND"
    }

    # 1) Buscar posible web oficial
    try:
        web_results = duckduckgo_html_search(f'{company} official website')
    except Exception as e:
        result["Status"] = f"SEARCH_ERROR_WEBSITE: {e}"
        return result

    official_url = None
    for r in web_results:
        if looks_like_official_website(company, r["url"], r["title"]):
            official_url = r["url"]
            break

    if official_url:
        meta = fetch_page_metadata(official_url)
        result["Website_found"] = meta["final_url"]
        result["Website_title"] = meta["title"]
        result["Website_description"] = meta["description"]

        combined_text = " ".join(filter(None, [
            meta["title"],
            meta["description"]
        ]))

        result["Industry_found"] = guess_industry(combined_text)
        result["Country_found"] = guess_country(combined_text)

    # 2) Buscar LinkedIn company page
    try:
        li_results = duckduckgo_html_search(f'site:linkedin.com/company "{company}"')
        for r in li_results:
            if is_linkedin_company(r["url"]):
                result["Linkedin_found"] = r["url"]
                break
    except Exception:
        pass

    if result["Website_found"] or result["Linkedin_found"]:
        result["Status"] = "PARTIAL_OK"

    if result["Website_found"] and result["Linkedin_found"] and (result["Industry_found"] or result["Country_found"]):
        result["Status"] = "OK"

    return result

def main():
    df = load_file(INPUT_FILE, SHEET_NAME)

    if COMPANY_COL not in df.columns:
        raise ValueError(f"No existe la columna '{COMPANY_COL}' en el archivo.")

    df[COMPANY_COL] = df[COMPANY_COL].apply(clean_company_name)
    df = df[df[COMPANY_COL].notna()].copy()

    enriched_rows = []

    for i, company in enumerate(df[COMPANY_COL].tolist(), start=1):
        print(f"[{i}/{len(df)}] Buscando: {company}")
        try:
            info = find_company_info(company)
        except Exception as e:
            info = {
                "Company": company,
                "Website_found": None,
                "Linkedin_found": None,
                "Industry_found": None,
                "Country_found": None,
                "Website_title": None,
                "Website_description": None,
                "Status": f"ERROR: {e}"
            }

        enriched_rows.append(info)
        time.sleep(DELAY_SECONDS)

    enriched_df = pd.DataFrame(enriched_rows)

    final_df = df.merge(enriched_df, on="Company", how="left")

    # Si quieres mapear a tus columnas originales:
    if "Website" in final_df.columns:
        final_df["Website"] = final_df["Website"].fillna(final_df["Website_found"])
    else:
        final_df["Website"] = final_df["Website_found"]

    if "Linkedin ." in final_df.columns:
        final_df["Linkedin ."] = final_df["Linkedin ."].fillna(final_df["Linkedin_found"])
    else:
        final_df["Linkedin ."] = final_df["Linkedin_found"]

    if "Industry" in final_df.columns:
        final_df["Industry"] = final_df["Industry"].fillna(final_df["Industry_found"])
    else:
        final_df["Industry"] = final_df["Industry_found"]

    if "País." in final_df.columns:
        final_df["País."] = final_df["País."].fillna(final_df["Country_found"])
    else:
        final_df["País."] = final_df["Country_found"]

    final_df.to_excel(OUTPUT_FILE, index=False)
    print(f"\nArchivo generado: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()