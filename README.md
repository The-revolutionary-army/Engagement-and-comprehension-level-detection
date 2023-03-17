# Engagemnet and Comprehension Level Detection
### Table of Contents. 
1. [Introduction](#introduction)
2. [Data Preprocessing](#data-preprocessing)
3. [Proposed System](#proposed-system)
    1. [Overview](#overview)
    2. [Attendance Module](#attendance-module)
    3. [Core Modules](#core-modules)
    4. [Comprehension Estimation](#comprehension-estimation)
4. [Application](#application)
5. [Future Work](#future-work)
6. [Acknowledgements](#acknowledgements)
8. [Authors](#authors)


---
## Introduction
During the COVID-19 pandemic, video conferencing applications faced the challenge of adapting to a significant increase in usage for remote work and education. The stability and effectiveness of these applications became crucial in retaining users. However, remote education presented a unique challenge for educators who previously relied on visual cues and in-person interactions to gauge student comprehension. The lack of these cues in virtual classrooms resulted in decreased interaction between students and educators.

This project aims to address this issue by utilizing artificial intelligence and advanced technology to improve virtual classroom interactions. The proposed solution involves developing a system that can analyze students’ facial expressions and behaviors to detect engagement, frustration, boredom, and confusion. This information can then be used to estimate student comprehension and provide feedback to educators.

The goal of this application is to bridge the gap between physical and virtual classrooms by providing educators with tools to enhance their ability to interact with students remotely.



---

## Data Preprocessing
The dataset comprises 9068 videos from 112 users. Face detection is the initial step in ensuring accurate model performance. The Histogram of Oriented Gradients (HOG) method in the DLIB Python library was utilized for face detection. The detected face was then cropped from the frame. DLIB provided an effective face detector; however, other options were considered before selecting this detector based on its advantages and disadvantages compared to others.

The image was resized to 48x48 pixels to facilitate rapid processing and conserve memory used for storing pickle files. Image enhancement techniques were applied to improve image clarity following face cropping in each frame. Contrast Limited Adaptive Histogram Equalization (CLAHE) was employed to enhance image features for the model by improving contrast.

Sequential processing of this large dataset was time-consuming, necessitating the implementation of parallel processing to expedite the task. A thread was assigned to each video for processing. The results were stored in pickle files after each video was processed. Pickle is a Python object used for rapid data storage and retrieval.



--- 

> ## Proposed System
## Overview
The proposed system utilizes webcam data to analyze student behavior during virtual lectures. Prior to using the system, users must agree to a privacy policy that prohibits the use of their data for commercial purposes.

The webcam data is processed through several stages including resizing, enhancement, and face detection. The resulting image is then fed into three modules: Attendance Recognition, Behavioral Analysis, and Comprehension Estimation.

The Attendance Recognition module verifies student presence in front of the device to facilitate accurate attendance tracking. The Behavioral Analysis module consists of four sub-models that detect engagement, boredom, frustration, and confusion. The output from these models is fed into the Comprehension Estimation module which determines student understanding during specific time intervals.

The results from all modules are periodically reported to the instructor to enable real-time adaptation to student needs and behaviors in a manner similar to physical classrooms.



---

## Attendance Module
The attendance module uses face recognition to identify students and create a report. The system takes pictures and checks identities based on facial features. The model is trained by comparing pictures and generates measurements called face embeddings. To identify students, previously measured faces are compared to find the closest match.




---

## Core Modules
The objective of this study was to develop a model that could classify the emotional state of a person within an image. The input for the model is a 48x48 grayscale image of the person’s face. During the training phase, several architectures were experimented with to address issues such as skewed class distribution and overfitting.

To address skewed class distribution, data augmentation and weighted class techniques were investigated. Four parallel convolutional neural networks (CNNs) were used for each emotional state (Engagement, Confusion, Frustration, and Boredom). Eventually, an all-convolutional net architecture was chosen for its accuracy in small details and its suitability for real-time detection of affective states. This architecture was modified by adding batch normalization and dropout to prevent overfitting.

During training, some problems were encountered such as exploding gradients in the stochastic gradient descent algorithm. The optimization algorithm was changed and the models were retrained. The final accuracies achieved with our successful models was: 
| Model | Accuracy |
| --- | --- |
| Engagement | 86.59% |
| Confusion | 82.08% |
| Frustration | 88.02% |
| Boredom | 74.30% |
| Overall | 82.50% |

[Parallel Model Architecture](./Models/parallel_model_architecture.pdf)



---

## Comprehension Estimation
Our approach to detecting student comprehension during lectures involves using Action Units (AUs) and the OpenFace toolkit. AUs are individual components of muscle movement that describe facial expressions. OpenFace is a toolkit capable of facial landmark detection, head pose estimation, facial action unit recognition, and eye-gaze estimation.

We integrated OpenFace with our system using Python bindings. Our approach to detecting student comprehension involves combining positive and negative AUs and states in an equation to determine the probability of comprehension. If engagement in a frame is zero this means that the term is cancelled because we considered that if a student is not engaged this means they cannot understand. But if they are engaged then there is a probability of comprehension.

The equation is as follows:
> $$ 
sgn(max(0, eng_i * \sum_{j=1}^{3}[(AU_{pos_j} + State_{pos_j}) - (AU_{neg_j} + State_{neg_j})]))
$$


| Variable           | Description |
| ------------------ | ----------- |
| eng                | The engagement in the current frame |
| AUPositive         | The positive action units (AU2, AU5, AU12) |
| AUNegative         | The negative action units (AU4, AU7, AU15) |
| StatePositive      | The positive states (Not Confused, Not Frustrated, Not Bored) |
| StateNegative      | The negative states (Confused, Frustrated, Bored) |



The role of maximize function (max) is to make value either zero for probability of non-comprehension or positive value for probability of comprehension. Then sign function takes new value and converts it to only zero and one so now we have 1 if probability of comprehension is high and zero if probability of non-comprehension is high.

After that we get average value of all these terms which gives us percentage of comprehension overall on specific time frame N.

If overall value exceeds specific threshold then we can say student understands lecture during this time frame otherwise we say they cannot understand.



---

## Application
The application uses Django for backend development and WebRTC for real-time video streaming between users. Django Channels creates a WebSocket endpoint for user connections. WebRTC enables web applications to capture/stream media and exchange data between browsers without intermediaries. The process involves obtaining browser information through signaling using the ICE protocol to generate media traversal candidates. A STUN server reveals the user’s public IP address for signaling other users. An offer is created with other users’ ICE candidates and sent through SDP. Once an agreement is reached between peers, a secure channel is established for sharing media.




---

## Future Work
Future work includes using pop-ups with instructor-defined questions to enhance the comprehension and engagement modules. Natural language processing (NLP) will be used to measure answer quality. A model will also be developed to predict student performance based on cumulative data.



---

## Acknowledgement
We would like to express our deepest appreciation to our project supervisor **Dr. Eman Abdel Ghaffar** for their invaluable guidance and support throughout our graduation project. Their expertise in human-computer interface and deep learning techniques has been instrumental in helping us tackle the challenges we faced. We are grateful for their encouragement and patience, which have inspired us to strive for excellence in our work. Thank you for being a wonderful mentor and for helping us achieve our goals.



---

## Authors
>* Omar Ali : [@OmarAli3](https://github.com/OmarAli3)
>* Mohammad Massoud : [@massoudsalem](https://github.com/massoudsalem)
>* Mohammad Ashraf : [@elhedeq](https://github.com/elhedeq)
>* Khalid Mahmoud : [@Khalid-MahmouD](https://github.com/Khalid-MahmouD)
>* Ahmed Hafez : [@Ahmed-Hafez](https://github.com/Ahmed-Hafez)
>* Mohammad Essam Elden : [@mo7amed-essam](https://github.com/mo7amed-essam)
