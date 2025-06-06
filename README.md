# CS-470 Topic-Specific Crawler Enhancement

This repository contains a team project for **KAIST CS470 (Introduction to Artificial Intelligence)**. Our goal was to extend and improve the research presented in a paper on a **BERT-Based Topic-Specific Crawler**.

---

## Project Overview

The original paper proposes a crawler that uses BERT to classify web pages based on their textual content. However, BERT has an input token limit of 512 tokens, which constrains its ability to fully understand longer documents.

Our project focuses on improving this approach in multiple ways:

- **Handling Long Texts:**
  We implemented chunk tokenization and content summarization methods to better capture the full meaning of web pages beyond the 512-token limit of BERT.

- **Multimodal Classification with CLIP:**
  We extended the model to use **CLIP**, which processes both text and images from a web page for classification. The goal is to improve classification by using image informations of the page.

- **Keyword-Based Image Filtering Pipeline:**
  Since directly using all images often introduced noise and degraded performance, we developed a new pipeline that:

  1. Performs a keyword-based web search.
  2. Scrapes the top 10 results.
  3. Filters images based on relevance to the keyword.
  4. Embeds filtered images and text for joint classification.

  This pipeline improved classification reliability by focusing on relevant images aligned with the page content.

---

## Repository Structure

- **`utility/`**
  Contains reusable utility functions developed separately for testing and integrated into the main pipeline notebooks.

- **`ModifiedBaseModel/`**
  Implements the baseline and improved versions following the original paper’s approach:

  - Multi-threaded web crawling and page classification.
  - Three notebooks:
    - **BERT-based notebook:** Adds chunk tokenization or summarization to better capture long page content beyond 512 tokens. Improves and fixes the base code of the paper.
    - **CLIP-based notebook:** Combines text and images for classification. Since no keyword is provided here, we cannot perform image filtering, which leads to many noisy images that reduce classification accuracy compared to text-only.
    - **Base model evaluator:** Improves the evaluation code of the paper, to test our improvement on the model, and have relevant result to compare. We use the same evulation process and dataset as in the paper.

- **`NewPipeline/`**
  Contains notebooks for the new keyword-driven pipeline:
  - **BERT-based notebook:** Uses the new pipeline with BERT, perform chunk tokenization or summarization on text content from keyword search results.
  - **CLIP-based notebook:** Uses the new pipeline with CLIP, using both filtered images and text content for classification, and also implements image filtering based on keywords to improve results.

---

## How to Run the Base Model Code

To run the base model code, simply execute the corresponding Jupyter notebook.

Before running the notebook, you need to modify the configuration object `conf` to match your environment and preferences. Here is an example configuration:

```python
conf = dict(
    dir = '/content/drive/My Drive/KAIST/Spider1/',
    imgsDir = "/content/drive/My Drive/KAIST/Spider1/imgs/",
    base_url = [
        'https://www.worldhistory.org',       # history
        'https://www.newworldencyclopedia.org/',  # history
        'https://www.ushistory.org',           # history
        'https://www.historic-uk.com/',        # history
        'https://hbr.org/',                     # business
        'https://newpol.org/',                  # politics
        'https://pc.net/',                      # technology
        'https://www.computerhope.com/',       # technology
        'https://www.computerlanguage.com/'    # technology
    ],
    number_of_threads = 9,
    labels = ['technology', 'business', 'politics', 'history'],
    blacklist = ['facebook', 'instagram', 'youtube'],
    mode = "summarize"
)

```

### Explanation of each configuration parameter:

- **`dir`**
  The root directory in Google Drive where all project data, including crawled content and outputs, will be stored.

- **`imgsDir`**
  The Google Drive directory specifically dedicated to saving images downloaded during the crawling process.

- **`base_url`**
  A list of seed URLs from which the crawler starts fetching web pages. These URLs are chosen based on the topics you want to classify (e.g., history, business, politics, technology). The crawler will follow links starting from these domains.

- **`number_of_threads`**
  Number of concurrent threads used for web crawling. You can use one thread for each url.

- **`labels`**
  The classification categories or topics corresponding to the seed URLs. The crawler and classifier will assign pages to one of these labels.

- **`blacklist`**
  List of domains or keywords that should be ignored during crawling to avoid irrelevant or noisy content, such as social media sites.

- **`mode`**
  Defines how to handle the page content text before classification. Supported modes include:
  - `"summarize"`: Summarize the entire page content to condense information.
  - `"chunk"`: Split content into chunks to handle BERT's token limit.

### Running the Notebook

After changing the configuration, you can run the notebook. The code will begin crawling and classifying web pages simultaneously using multithreading.

- The crawling process and classification run concurrently.
- All data and outputs are automatically saved in a CSV file located in the root directory you specified in the configuration (`dir`).
- This crawler is **recursive** and **infinite**, it continuously discovers new links and refreshes its crawl daily.
- The CSV file is **updated in real time**, so you can inspect the results as the crawler runs.

### Evaluating the Results of the Base Model

Since the major part of our work consisted of improving the Base Model and we provided evaluation results on this Model, we provide the evaluation code for this Model only. 
To evaluate the classification performance:

1. Open the `base_model_evaluator` notebook.
2. Modify the path to point to your own CSV result file.
3. If you are using your own dataset or domains, update the domain-to-category mapping accordingly.

This will allow you to analyze how well the model is classifying each crawled page.

## How to Run the New Pipeline Code

![new_pipeline_graph](https://github.com/user-attachments/assets/fe78d162-5f14-4d33-9011-928a5e2d7707)

We provide the code for our proposed New Pipeline described in the poster. This is a prototype build that is runnable, but leaves space for future improvement and further modification. Since we implemented a live Web search module, evaluation of this system involves a curation of a large test set, which is a part of our nearest future works.

Just like the base model, you need to update the configuration before running the notebook:

```python
conf = dict(
    dir = '/content/drive/My Drive/KAIST/Spider1/',
    imgsDir = "/content/drive/My Drive/KAIST/Spider1/imgs/",
    keywords = ['Elon Musk', 'Tour Eiffel'],
    labels = ['technology','business','politics', 'history'],
    blacklist = ['youtube.com', 'facebook.com',
                   'twitter.com', 'x.com', 'instagram.com', 'linkedin.com','tiktok.com'],
    mode = "summarize",
    image_weight = 0.3
)
```

- **`keywords`**
  A list of topic-specific search terms. For each keyword, a web search is performed, and the top search result links are used as input for classification.
  These keywords are also used to filter images: only images relevant to the keyword are selected for classification when using the CLIP-based model.

- **`labels`**
  Categories or topics used for classifying the crawled pages. These should align with your use case or dataset.

- **`image_weight`**
  A float value between 0 and 1 that controls the influence of image weight in the classification when using CLIP.

### Running the New Pipeline

Once the configuration is updated:

- The notebook will perform a web search for each keyword.
- It collects the top 10 links from the search results.
- For each link, the page content is scraped sequentially.
- The notebook applies chunk tokenization or summarization to handle long text inputs for models like BERT.
- If using CLIP, it will download and filter images based on their relevance to the keyword, reducing noise from irrelevant visuals.
- Both the text and the relevant images are embedded and passed to the model for classification.
- The classification results are saved in a JSON file located in the `dir` you specified.
  In the output, each link is grouped by its predicted label, helping the user easily identify the most relevant pages for a given search keyword.

```json
{
	"technology": ["https://example.com/elon-musk-interview"],
	"history": ["https://example.com/tour-eiffel-architecture"]
}
```

## Future Improvements

Current system only utilizes pre-trained models, so it is advisable to finetune both CLIP or SBERT on your specific domain or use case. To overcome the limitations of CLIP and improve both text and image embedding quality, it is worth exploring utilization of separate CNN instead of CLIP, however some limitation to watch out for include difficulty of communication between separate models. Some more robust filters for image and text content of scraped pages could improve extraction and classification quality. Since the current system only scrapes the top-N search resutls of the Web search, it is worth experimenting with internal search of each results for the pages that align with the search query for a deeper scraping performance. 

## Team

This project was developed by the KAIST CS470 team #15.

20256086 Julien Dupont

20244673 Aleksandra Pshenova

20256098 Matthew Heffernan

20220862 Nuradil Zhambyl
