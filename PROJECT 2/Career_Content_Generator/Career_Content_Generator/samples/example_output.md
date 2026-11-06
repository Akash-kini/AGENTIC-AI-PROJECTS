# Career Profile: Aarav Sharma

*Generated 2026-11-06T10:05:48 using SIMULATED-EXAMPLE (offline stub, not a live Gemini call)*

## Student Overview

- **Degree:** B.Tech in Computer Science and Engineering
- **Academic interests:** Artificial Intelligence, Machine Learning
- **Technical skills:** Python, NumPy, SQL
- **Experience level:** Beginner
- **Career goal:** AI Engineer

## Professional Summary

Computer Science and Engineering student pursuing a B.Tech with a strong interest in Artificial Intelligence and Machine Learning. Has a foundation in Python, NumPy and SQL and is building toward an entry-level AI Engineer role. Currently at a beginner level and focused on learning core machine learning and deep learning fundamentals through structured study and hands-on projects.

## Skill-Gap Report

**Target role:** AI Engineer

The student has useful programming and data foundations but is at the start of the machine learning path. With consistent study over roughly six months, an entry-level AI Engineer profile is realistic.

### Existing Skills

| Skill | Relevance to goal | Note |
|---|---|---|
| Python | high | Primary language for ML and AI development. |
| NumPy | high | Core library for numerical computing and array operations used in ML. |
| SQL | medium | Useful for querying and preparing data for models. |

### Missing Skills

| Skill | Importance | Why it is needed |
|---|---|---|
| Pandas and Data Wrangling | critical | Real-world datasets must be cleaned and explored before modelling. |
| Statistics and Probability | critical | Underpins model evaluation and ML theory. |
| Linear Algebra and Calculus Basics | important | Needed to understand how models learn. |
| Machine Learning with scikit-learn | critical | Standard toolkit for classical ML models. |
| Deep Learning with PyTorch | critical | Most AI Engineer roles build and fine-tune neural networks. |
| Git and GitHub | important | Version control is expected in every engineering team. |
| Model Deployment (FastAPI, Docker) | important | AI Engineers ship models as services. |
| Large Language Models and Prompting | nice to have | Increasingly common in AI Engineer job descriptions. |

## Learning Recommendations

### Recommended Courses and Resources

*Please verify availability and details before enrolling.*

- **Machine Learning Specialization** - DeepLearning.AI on Coursera (Beginner). A well-known beginner-friendly introduction to core ML concepts. Covers: Machine Learning with scikit-learn, Statistics and Probability.
- **Practical Deep Learning for Coders** - fast.ai (Intermediate). Hands-on, project-first introduction to deep learning. Covers: Deep Learning with PyTorch.
- **Kaggle Learn: Pandas and Intro to Machine Learning** - Kaggle (Beginner). Short, free, practical lessons with exercises. Covers: Pandas and Data Wrangling.
- **Mathematics for Machine Learning** - Imperial College London on Coursera (Beginner). Covers the maths behind ML. Covers: Linear Algebra and Calculus Basics.
- **PyTorch official tutorials** - pytorch.org (Intermediate). Authoritative, up-to-date practical guides. Covers: Deep Learning with PyTorch.
- **Pro Git** - git-scm.com (free book) (Beginner). The standard reference for version control. Covers: Git and GitHub.

### Key Learning Topics

- **Data analysis with Pandas** - Almost every ML project starts with data cleaning. _(DataFrames, missing values, group-by, visualisation)_
- **Statistics and probability** - Needed to evaluate models correctly. _(distributions, hypothesis testing, bias and variance)_
- **Classical machine learning** - Foundation before deep learning. _(regression, classification, cross-validation, metrics)_
- **Neural networks and deep learning** - Core of modern AI engineering. _(backpropagation, CNNs, training loops, regularisation)_
- **Model deployment basics** - Models only create value when served. _(REST APIs, FastAPI, containers)_

## Personalized Learning Roadmap

### Phase 1: Strengthen data foundations (Weeks 1-4)

**Goals:**
- Use Pandas fluently
- Visualise datasets

**Topics:** Pandas, Matplotlib, SQL joins revisited

**Milestone project:** Exploratory data analysis of a public dataset using Python, NumPy, Pandas and SQL

### Phase 2: Maths and statistics for ML (Weeks 5-8)

**Goals:**
- Understand vectors, matrices and gradients
- Apply basic statistics

**Topics:** Linear algebra, Probability, Descriptive statistics

**Milestone project:** Implement linear regression from scratch with NumPy

### Phase 3: Classical machine learning (Weeks 9-14)

**Goals:**
- Train and evaluate models
- Avoid overfitting

**Topics:** scikit-learn, Model evaluation, Feature engineering

**Milestone project:** End-to-end classification project with a written evaluation

### Phase 4: Deep learning fundamentals (Weeks 15-20)

**Goals:**
- Build and train neural networks in PyTorch

**Topics:** PyTorch, CNNs, Training loops

**Milestone project:** Image classifier trained in PyTorch

### Phase 5: Engineering and deployment (Weeks 21-26)

**Goals:**
- Version code with Git
- Serve a model through an API

**Topics:** Git and GitHub, FastAPI, Docker basics

**Milestone project:** Deploy the image classifier as a simple web API and publish it on GitHub

## Technical Interview Questions and Answers

**Q1. What is the difference between supervised and unsupervised learning?** _[Beginner - ML basics]_

**A:** Supervised learning trains on labelled examples to predict a target, such as classification or regression. Unsupervised learning finds structure in unlabelled data, such as clustering or dimensionality reduction.

**Q2. Why does NumPy make numerical code faster than plain Python lists?** _[Beginner - NumPy]_

**A:** NumPy stores homogeneous data in contiguous memory and runs vectorised operations in compiled C code. This avoids Python-level loops and per-element object overhead.

**Q3. What is overfitting and how can you reduce it?** _[Beginner - ML basics]_

**A:** Overfitting is when a model memorises training data and performs poorly on new data. It can be reduced with more data, simpler models, regularisation, cross-validation and early stopping.

**Q4. Explain the train, validation and test split.** _[Beginner - Evaluation]_

**A:** Training data fits the model, validation data is used to tune hyperparameters, and the test set gives a final unbiased estimate of performance. The test set should only be used once at the end.

**Q5. When would you use precision and recall instead of accuracy?** _[Beginner - Metrics]_

**A:** On imbalanced data accuracy can be misleading. Precision measures how many predicted positives are correct, and recall measures how many real positives are found, so they reveal errors accuracy hides.

**Q6. Write the SQL idea behind finding the top 5 customers by total spend.** _[Beginner - SQL]_

**A:** Group the orders by customer, sum the amount for each group, sort the totals in descending order and limit the result to five rows. A join with the customers table adds their names.

**Q7. What is gradient descent?** _[Intermediate - Optimisation]_

**A:** Gradient descent is an iterative algorithm that updates model parameters in the direction that reduces the loss, using the gradient of the loss. The learning rate controls the step size.

**Q8. What is the bias-variance trade-off?** _[Intermediate - ML theory]_

**A:** Bias is error from overly simple assumptions and variance is error from sensitivity to training data. Increasing model complexity usually lowers bias but raises variance, so you look for a balance that generalises well.

**Q9. How does a convolutional neural network differ from a fully connected network?** _[Intermediate - Deep learning]_

**A:** A CNN shares small learned filters across the image, which captures local patterns with far fewer parameters and some translation invariance. A fully connected network connects every input to every neuron and ignores spatial structure.

**Q10. How would you serve a trained model to other applications?** _[Intermediate - Deployment]_

**A:** Save the trained model, load it in a web service such as FastAPI that exposes a prediction endpoint, validate incoming data, and package it in a container so it runs the same way everywhere.

## Resume-Ready Content

**Aspiring AI Engineer | B.Tech in Computer Science and Engineering**

### Summary

Computer Science undergraduate focused on Artificial Intelligence and Machine Learning, with working knowledge of Python, NumPy and SQL. Following a structured plan to build machine learning and deep learning skills through hands-on projects.

### Skills

- **Technical skills:** Python, NumPy, SQL
- **Currently learning:** Pandas and Data Wrangling, Machine Learning with scikit-learn, Deep Learning with PyTorch, Git and GitHub

### Education

- B.Tech in Computer Science and Engineering

### Experience

No professional experience yet; seeking an entry-level opportunity and building a portfolio through academic and self-directed projects.

### Suggested Portfolio Projects

*These are SUGGESTED portfolio projects. Add them to a resume only after you have actually built them.*

**Exploratory Data Analysis of a Public Dataset** - Python, NumPy, SQL, Pandas and Data Wrangling

Clean, query and summarise a public dataset and report the main findings.

- Cleaned and explored a public dataset using Python and NumPy to uncover key trends
- Wrote SQL queries to aggregate and filter records for analysis
- Documented findings in a clear, reproducible notebook

**Linear Regression from Scratch** - Python, NumPy

Implement linear regression with gradient descent using only NumPy.

- Implemented linear regression and gradient descent from scratch using NumPy
- Compared results against a library implementation to validate correctness

**Image Classifier with PyTorch** - Python, Deep Learning with PyTorch, Git and GitHub

Train a small convolutional network to classify images and evaluate it.

- Built and trained a convolutional neural network for image classification in PyTorch
- Evaluated the model with accuracy and a confusion matrix and tracked code on GitHub

## Consistency Checks

- [PASS] Existing skills match the skills the student entered
- [PASS] No skill appears as both existing and missing
- [PASS] Resume technical skills only list the student's skills
- [PASS] No senior/professional-experience claims for a Beginner
- [PASS] Project tech stacks only use existing or roadmap skills
