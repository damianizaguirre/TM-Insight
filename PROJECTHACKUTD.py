import praw
import requests
import json
import re
import csv
import numpy as np
from sklearn.cluster import KMeans

# Reddit API Setup
reddit = praw.Reddit(
    client_id="aZA0e20-zSJGOoYHCt5bMw",
    client_secret="-vr3OfJcFVg0AP5MsVXWft5jE7buFg",
    user_agent="tmobile_texas_sentiment"
)

# OpenRouter API Setup
OPENROUTER_API_KEY = "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"
MODEL = "openai/gpt-3.5-turbo"

MAX_EXPECTED_OUTAGES = 500
MAX_FEEDBACK_EXPECTED = 10

# Texas Counties
TEXAS_COUNTIES = [
    "Anderson","Andrews","Angelina","Aransas","Archer","Armstrong","Atascosa","Austin",
    "Bailey","Bandera","Bastrop","Baylor","Bee","Bell","Bexar","Blanco","Borden","Bosque",
    "Bowie","Brazoria","Brazos","Brewster","Briscoe","Brooks","Brown","Burleson","Burnet",
    "Caldwell","Calhoun","Callahan","Cameron","Camp","Carson","Cass","Castro","Chambers",
    "Cherokee","Childress","Clay","Cochran","Coke","Coleman","Collin","Collingsworth","Colorado",
    "Comal","Comanche","Concho","Cooke","Coryell","Cottle","Crane","Crockett","Crosby","Culberson",
    "Dallam","Dallas","Dawson","Deaf Smith","Delta","Denton","DeWitt","Dickens","Dimmit","Donley",
    "Duval","Eastland","Ector","Edwards","Ellis","El Paso","Erath","Falls","Fannin","Fayette",
    "Fisher","Floyd","Foard","Fort Bend","Franklin","Freestone","Frio","Gaines","Galveston",
    "Garcia","Garza","Gillespie","Glasscock","Goliad","Gonzales","Gray","Grayson","Gregg",
    "Grimes","Guadalupe","Hale","Hall","Hamilton","Hansford","Hardeman","Hardin","Harris",
    "Harrison","Hartley","Haskell","Hays","Hemphill","Henderson","Hidalgo","Hill","Hockley",
    "Hood","Hopkins","Houston","Howard","Hudspeth","Hunt","Hutchinson","Irion","Jack","Jackson",
    "Jasper","Jeff Davis","Jefferson","Jim Hogg","Jim Wells","Johnson","Jones","Karnes","Kaufman",
    "Kendall","Kenedy","Kent","Kerr","Kimble","King","Kinney","Kleberg","Knox","Lamar","Lamb",
    "Lampasas","La Salle","Lavaca","Lee","Leon","Liberty","Limestone","Lipscomb","Live Oak","Llano",
    "Loving","Lubbock","Lynn","McCulloch","McLennan","McMullen","Madison","Marion","Martin","Mason",
    "Matagorda","Maverick","Medina","Menard","Midland","Milam","Mills","Mitchell","Montague","Montgomery",
    "Moore","Morris","Motley","Nacogdoches","Navarro","Newton","Nolan","Nueces","Ochiltree","Oldham",
    "Orange","Palo Pinto","Panola","Parker","Parmer","Pecos","Polk","Potter","Presidio","Rains","Randall",
    "Reagan","Real","Red River","Reeves","Refugio","Roberts","Robertson","Rockwall","Runnels","Rusk",
    "Sabine","San Augustine","San Jacinto","San Patricio","San Saba","Schleicher","Scurry","Shackelford",
    "Shelby","Sherman","Smith","Somervell","Starr","Stephens","Sterling","Stonewall","Sutton","Swisher",
    "Tarrant","Taylor","Terrell","Terry","Throckmorton","Titus","Tom Green","Travis","Trinity","Tyler",
    "Upshur","Upton","Uvalde","Val Verde","Van Zandt","Victoria","Walker","Waller","Ward","Washington",
    "Webb","Wharton","Wheeler","Wichita","Wilbarger","Willacy","Williamson","Wilson","Winkler","Wise",
    "Wood","Yoakum","Young","Zapata","Zavala", "Unknown"
]


# Functions:
def extract_relevant_sentences(text):
    sentences = re.split(r'[.!?]\s+', text)
    relevant = []
    for sentence in sentences:
        if "texas" in sentence.lower() or "tx" in sentence.lower():
            relevant.append(sentence)
        else:
            for county in TEXAS_COUNTIES:
                if county.lower() in sentence.lower():
                    relevant.append(sentence)
                    break
    return " ".join(relevant) if relevant else text

def analyze_post(text):
    relevant_text = extract_relevant_sentences(text)
    prompt = f"""
    Analyze the following Reddit post and provide:
    1. Sentiment: Positive, Negative, or Neutral
    2. Texas County mentioned in the post (if any; otherwise 'Unknown')

    Post: \"\"\"{relevant_text}\"\"\"

    Respond in JSON format like this:
    {{
        "sentiment": "<Positive|Negative|Neutral>",
        "county": "<County name or 'Unknown'>"
    }}
    """
    headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
    data = {"model": MODEL, "messages": [{"role": "user", "content": prompt}], "max_output_tokens": 200}
    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
        result = response.json()
        output_text = result["choices"][0]["message"]["content"]
        parsed = json.loads(output_text)
        return {
            "sentiment": parsed.get("sentiment", "Neutral"),
            "county": parsed.get("county", "Unknown")
        }
    except Exception as e:
        print("Error analyzing post:", e)
        return {"sentiment": "Neutral", "county": "Unknown"}

def sentiment_to_score(sentiment: str) -> float:
    mapping = {"Positive": 1.0, "Neutral": 0.5, "Negative": 0.0}
    return mapping.get(sentiment, 0.5)

def fetch_county_outage_count(county_name: str) -> int:
    return np.random.randint(0, 50)

def compute_feedback_volume(feedback_list: list) -> float:
    return min(len(feedback_list)/MAX_FEEDBACK_EXPECTED, 1.0)

def generate_ai_solution_openrouter(county_name, cluster_label, weighted_sentiment, weighted_network, weighted_feedback, happiness_score):
    prompt = f"""
    You are a telecom customer experience expert.
    County: {county_name}
    Cluster: {cluster_label}
    Weighted Sentiment: {weighted_sentiment:.2f}
    Weighted Network: {weighted_network:.2f}
    Weighted Feedback: {weighted_feedback:.2f}
    Happiness Score: {happiness_score:.2f} (0-100)

    Provide a concise, actionable recommendation for T-Mobile to improve customer happiness in this county.
    """
    headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
    data = {"model": MODEL, "messages": [{"role": "user", "content": prompt}], "temperature": 0.7}
    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
        result = response.json()
        solution = result.get("choices", [{}])[0].get("message", {}).get("content", "No recommendation available.").strip()
        return solution
    except Exception as e:
        print(f"Error generating AI solution for {county_name}: {e}")
        return "No recommendation available."

def main():
    #Fetch Reddit posts
    subreddit_name = "tmobile"
    query = "Texas T-Mobile"
    limit = 50
    posts = reddit.subreddit(subreddit_name).search(query, limit=limit, sort="new")

    #Gather feedback by county
    county_feedback: dict[str, list[dict]] = {}
    for post in posts:
        text = post.title + " " + (post.selftext or "")
        result = analyze_post(text)
        county = result["county"]
        sentiment = result["sentiment"]
        county_feedback.setdefault(county, []).append({"text": text, "sentiment": sentiment})

    #Compute county happiness
    county_results = []
    statewide_happiness_scores = []

    for county in TEXAS_COUNTIES:
        feedbacks = county_feedback.get(county, [])
        # Sentiment score normalization
        if feedbacks:
            S_raw = sum([sentiment_to_score(fb["sentiment"]) for fb in feedbacks]) / len(feedbacks)
        else:
            S_raw = 0.5
        S = min(max(S_raw, 0.0), 1.0)  # normalize to 0-1

        # Network reliability
        N_raw = max(0.0, 1.0 - fetch_county_outage_count(county)/MAX_EXPECTED_OUTAGES)
        N = min(max(N_raw, 0.0), 1.0)

        # Feedback volume
        F_raw = compute_feedback_volume(feedbacks) if feedbacks else 0.0
        F = min(max(F_raw, 0.0), 1.0)

        WeightedSentiment = 0.6 * S * 100
        WeightedNetwork = 0.3 * N * 100
        WeightedFeedback = 0.1 * F * 100
        H = WeightedSentiment + WeightedNetwork + WeightedFeedback

        county_results.append({
            "County": county,
            "WeightedSentiment": round(WeightedSentiment, 2),
            "WeightedNetwork": round(WeightedNetwork, 2),
            "WeightedFeedback": round(WeightedFeedback, 2),
            "HappinessScore": round(H, 2)
        })
        statewide_happiness_scores.append(H)

    # Clustering
    X = np.array([[c["WeightedSentiment"], c["WeightedNetwork"], c["WeightedFeedback"]] for c in county_results])
    kmeans = KMeans(n_clusters=4, random_state=42)
    labels = kmeans.fit_predict(X)

    for i, county in enumerate(county_results):
        county["Cluster"] = int(labels[i])
        H = county["HappinessScore"]
        if H >= 80:
            cluster_label = "High Happiness"
        elif H >= 60:
            cluster_label = "Moderate Happiness"
        elif H >= 40:
            cluster_label = "Low Happiness"
        else:
            cluster_label = "Very Low Happiness"
        county["ClusterLabel"] = cluster_label

        # Generate AI recommendation
        county["Recommendation"] = generate_ai_solution_openrouter(
            county_name=county["County"],
            cluster_label=cluster_label,
            weighted_sentiment=county["WeightedSentiment"],
            weighted_network=county["WeightedNetwork"],
            weighted_feedback=county["WeightedFeedback"],
            happiness_score=H
        )

    # Save as CSV
    csv_file = "county_happiness_with_reddit_feedback_normalized.csv"
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "County","WeightedSentiment","WeightedNetwork","WeightedFeedback",
            "HappinessScore","Cluster","ClusterLabel","Recommendation"
        ])
        writer.writeheader()
        writer.writerows(county_results)

    statewide_H = sum(statewide_happiness_scores)/len(statewide_happiness_scores) if statewide_happiness_scores else 0.0
    print(f"CSV saved: {csv_file}")
    print(f"Statewide Customer Happiness Index (0-100): {round(statewide_H,2)}")

if __name__ == "__main__":
    main()
