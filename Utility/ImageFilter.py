# Check if we have GPU available
device = "cuda" if torch.cuda.is_available() else "cpu"
# Initialize the model (CLIP)
model, preprocess = clip.load("ViT-B/32", device=device)

"""STEP 1 -- Page relevance filter
Here we check the relevance of Web Search output URL to search keyword. We need to connect this function to the Web Searcher module to take the keyword and list of URLs (or dict, whatever format there is)
---
** Update **
---
This layer is supposed to work if we scrape the initial 10 URLs we got from Web search with the recusrive scraper from the original paper. If we omit this step and only classify the 10 seed URLs, then we can go directly to Step 2 (image relevance), since all 10 result URLs are related to the search keyword (otherwise how would they pop up as a search result). In fact, they are the MOST elevant URLs to the search query, since they are top-10.
"""


def check_text_relevance(page_text: str, keyword: str, threshold: float = 0.25) -> bool:
    # clean up the scraped HTML text (can add more clean up functions)
    page_text = re.sub(r"\s+", " ", page_text)
    # tokenize page text and keyword
    inputs = clip.tokenize([page_text, keyword]).to(device)
    with torch.no_grad():
        embeddings = model.encode_text(inputs)
    # check cosine similarity and only let the URLs that are above threshold (custom)
    sim = cosine_similarity([embeddings[0].cpu().numpy()], [
                            embeddings[1].cpu().numpy()])[0][0]
    return sim >= threshold


"""STEP 2 -- Image relevance filter
Here whe check the image relevance to the content of  the pages that are filtered with step 1.
"""

# Save folders inside Colab for images before and after filtering
# (put your own path here)
RAW_DIR = ""
FILTERED_DIR = ""

os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(FILTERED_DIR, exist_ok=True)


def hash_url(url: str):
    return hashlib.md5(url.encode()).hexdigest()[:12]


def save_image_to_disk(image: Image.Image, folder: str, prefix: str, idx: int) -> str:
    path = os.path.join(folder, f"{prefix}_img{idx}.jpg")
    image.save(path)
    return path


def get_image_relevance(image_path: str, keyword_embed: torch.Tensor,
                        prefix: str, idx: int, image_threshold: float = 0.3):
    try:
        # response = requests.get(image_url, timeout=5)
        # image = Image.open(BytesIO(response.content)).convert("RGB")

        # Save raw image
        # raw_path = save_image_to_disk(image, RAW_DIR, prefix, idx)

        try:
            image = Image.open(image_path).convert("RGB")
            if img.mode == 'P':
                img = img.convert('RGBA')
            else:
                img = img.convert('RGB')
        except:
            print(f"Skipped file {path}")

        # Embed and score
        image_input = preprocess(image).unsqueeze(0).to(device)
        with torch.no_grad():
            image_embed = model.encode_image(image_input).squeeze()
            sim = cosine_similarity(
                [image_embed.cpu().numpy()],
                [keyword_embed.cpu().numpy()]
            )[0][0]

        # Save filtered if relevant (threshold is adjustable)
        if sim >= image_threshold:
            filtered_path = save_image_to_disk(
                image, FILTERED_DIR, prefix, idx)
        else:
            filtered_path = None

        return sim, image_embed, filtered_path
    except Exception as e:
        print(f"Error for {image_url}: {e}")
        return None


"""Helper function: Deduplicate embeddings to get rid of identical images (threshold is adjustable, this way we get rid of very similar images)"""


def deduplicate_embeddings(image_embeds: list[torch.Tensor], threshold: float = 0.95) -> list[int]:
    if not image_embeds:
        return []
    vectors = torch.stack(image_embeds).cpu().numpy()
    sim_matrix = cosine_similarity(vectors)
    keep_indices = []
    discarded = set()

    for i in range(len(vectors)):
        if i in discarded:
            continue
        keep_indices.append(i)
        for j in range(i + 1, len(vectors)):
            if sim_matrix[i][j] >= threshold:
                discarded.add(j)
    return keep_indices


"""Final function: Assemble everything in one single function that processes Search results URL"""

# takes text, kw, list of URLs as input, returns Dict of both text, url, and images
# --> can be directly plugged in our classifier


def process_page(url: str, keyword: str,
                 text_threshold=0.25, image_threshold=0.3, max_images=5):
    try:
        # response = requests.get(url, timeout=10)
        # soup = BeautifulSoup(response.text, "html.parser")
        # text = ' '.join(p.get_text() for p in soup.find_all("p"))

        # relevance check
        if not check_text_relevance(text, keyword, threshold=text_threshold):
            print(f"Skipped (text not relevant): {url}")
            return None

        print(f"Processing: {url}")
        image_tags = soup.find_all("img")
        image_urls = [urljoin(url, img.get("src"))
                      for img in image_tags if img.get("src")]
        keyword_embed = model.encode_text(
            clip.tokenize([keyword]).to(device)).squeeze()

        embeds_and_paths = []
        for idx, img_url in enumerate(image_urls[:max_images * 2]):
            result = get_image_relevance(
                img_url, keyword_embed, hash_url(url), idx, image_threshold)
            if result is None:
                continue
            sim, emb, filtered_path = result
            if filtered_path:
                embeds_and_paths.append((emb, filtered_path))

        if not embeds_and_paths:
            return None

        # Deduplicate
        image_embeds = [e for e, _ in embeds_and_paths]
        keep_idxs = deduplicate_embeddings(image_embeds)
        kept_embeds = [image_embeds[i] for i in keep_idxs]
        kept_paths = [embeds_and_paths[i][1] for i in keep_idxs]

        return {
            "url": url,
            "text": text,
            "image_embeds": kept_embeds,
            "image_paths": kept_paths
        }

    except Exception as e:
        print(f"[!] Failed: {url} | {e}")
        return None
