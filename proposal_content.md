# Early Product Success from Amazon Reviews

Assignment 6 proposal - English content source

## 1  The user, the decision, and what already exists

**User and decision.** Maya is a small Amazon beauty seller whose product has just received its 20th review. She must decide whether to place another inventory order and continue advertising. Today she relies on the average star rating. Our Streamlit app will estimate the probability of strong review performance over the next year and compare early-review patterns with historical peers. If the outlook is weak, she would defer a large reorder, inspect recurring complaints, and run a smaller test; a stronger outlook would prompt a reorder review using her own margin and sales data.

**Existing tools.** [Jungle Scout Historical Trends](https://support.junglescout.com/hc/en-us/articles/4413674924311-Historical-Trends-Graph-on-the-Product-Listing-page) shows price, rank, estimated unit sales, and review trends. This helps with market context, but its documented workflow does not establish a first-20-reviews forecast for our defined one-year outcome. [Helium 10 Review Insights](https://kb.helium10.com/hc/en-us/articles/48006601967643-Review-Insights-Analyze-Customer-Feedback-with-Amazon-Data) summarizes review topics, sentiment trends, and category comparisons. It helps identify complaints, but its documented output does not estimate our future success label. Our distinction is a fixed early-review cutoff, a testable outcome, and a held-out baseline; these are proposed differences based on the linked documentation.

## 2  Data reality check

**Sources and unit.** We loaded McAuley Lab's [Amazon Reviews 2023](https://amazon-reviews-2023.github.io/) [All_Beauty reviews](https://mcauleylab.ucsd.edu/public_datasets/data/amazon_2023/raw/review_categories/All_Beauty.jsonl.gz) and [product metadata](https://mcauleylab.ucsd.edu/public_datasets/data/amazon_2023/raw/meta_categories/meta_All_Beauty.jsonl.gz). The raw review file contains **701,528 reviews for 112,565 parent products**; metadata contains 112,590 products. Reviews span November 2000 to September 2023. Removing 7,275 exact duplicate records leaves 694,253 reviews. A modeling row is one **parent_asin** (including its variants), summarized at its 20th distinct review. Requiring 20 reviews and a 365-day observation window before the dataset endpoint leaves **5,709 products**. Metadata supplies display titles only.

**Target distribution.** Using the training-derived rule in Section 3, 836 products (14.6%) meet the proxy and 4,873 (85.4%) do not. This is the full eligible cohort; the test set has a 15.5% positive rate.

**One random row.** Sampling the product table with seed 42 selects **B01ETUB7Q2**, a men's cologne. By September 20, 2018, its first 20 reviews averaged 4.05 stars, 75% were verified purchases, and 846 days had passed since its first review. In the following 365 days, it received 9 reviews averaging 3.78 stars, so **is_successful = 0**. This row describes one product's early signals and later observed review outcome.

**Surprise and change of plan.** Exact duplicate reviews changed eligibility: the original idea's 5,787 examples become 5,709 after cleaning. Also, the median time to review 20 is **339 days**. We therefore describe this as early in review history, not necessarily early after launch. The revised label rate also reflects a training-only volume threshold.

## 3  Target, metric, and baseline

**Target.** **is_successful** is a derived binary classification column in our product table, not a supplied raw field. It equals 1 if reviews strictly after review 20 and within the next **365 days** number at least **24** and average at least **4.0 stars**; otherwise it is 0. The 24-review cutoff is the training set's 75th percentile, with ties included, and is fixed for testing. No later reviews means label 0. This measures review traction and satisfaction, not sales or profit.

**Evaluation.** Following Assignment 5, we split unique products **70/30, seed 42** before choosing the volume threshold: **3,996 train / 1,713 test**, without stratification. Primary metric: **balanced accuracy**, the average of success recall and non-success recall; it prevents the majority class from dominating the score. We will also report success precision and recall because false positives can encourage costly reorders. Feature fitting and threshold selection will use training cross-validation; this baseline test set is reserved for final model comparison.

**No-input baseline, actually run.** Always predicting the training majority class (0) gives test **balanced accuracy = 0.500**, accuracy = **84.47%**, and success recall = **0%**. It correctly labels 1,447 negatives and misses all 266 positives. This is the required score to beat; a high raw accuracy alone is not sufficient.

## 4  Predictions before you model

**Three expected inputs.** (1) **early_rating_mean**: satisfaction in the first 20 reviews may persist. (2) **days_to_20**: faster review accumulation may signal stronger demand. (3) **early_text**: TF-IDF features from the first 20 review texts may distinguish repeat-purchase praise from defects beyond the star average. Verified-purchase share will be an additional candidate; category is constant in this first version.

**Prediction, not a measured result.** Before fitting feature-based models, we expect our best model to reach **0.65-0.70 balanced accuracy**, or **15-20 percentage points** above the 0.50 baseline. Ratings and review timing should carry signal, but missing sales, advertising, and stockout information should limit performance. We will compare regularized logistic regression with structured-feature tree models; no feature-based model has been trained for this proposal.

## 5  App walkthrough

Maya uploads the complete first 20 reviews (rating, text, date, verified-purchase flag) for one parent product, or selects a historical demo. The app validates the fields and cutoff, then displays the estimated **probability of meeting the review-success proxy**, the training cohort's 14.3% reference rate, and influential early signals. It will show calibration evidence before treating scores as probabilities. Maya inspects complaints and compares peers before choosing a small test or a reorder review; the app does not calculate order quantities.

In **Explore**, she filters historical training products by early rating and days to review 20, browses text-based peer groups, and sees each group's size and observed success share. She can learn that favorable early stars alone need not imply sustained review volume. These are associations, not evidence that changing reviews causes success. Page 3 sketches both tabs and their flow.

## 6  Risks and team plan

**Main risk.** The review proxy may not match the seller's business outcome, and products that never reach 20 reviews are excluded. We will state this limit, test alternative label thresholds using training data, and seek seller feedback. To reduce leakage, we exclude helpful votes, price, and metadata rating totals because their cutoff-time values are unavailable. A later chronological check will train only on products whose 365-day outcomes finish before the test cutoff; older 2000-2023 data still limits current-market claims.

**Ownership over three weeks.** **Team lead (me)** will do the main implementation: Week 1, cleaning, labels, baseline and features; Week 2, modeling and evaluation; Week 3, Streamlit integration and final report. **Other teammates** will support prior-tool research (Week 1), exploratory charts (Week 2), and usability testing and proofreading (Week 3). Their individual assignments remain to be confirmed. Everyone reviews the final claims and demo.
