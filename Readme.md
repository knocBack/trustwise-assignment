# Trustwise Take Away Assignment Repository
This repository contains an trustwise take-away assignment that demonstrates 5 scores as mentioned in the assignment, 
namely [vectara](https://huggingface.co/vectara/hallucination_evaluation_model), [toxicity](https://huggingface.co/s-nlp/roberta_toxicity_classifier), [emotion](https://huggingface.co/SamLowe/roberta-base-go_emotions), [gibberish](https://huggingface.co/wajidlinux99/gibberish-text-detector) & [old gibberish repo](https://huggingface.co/madhurjindal/autonlp-Gibberish-Detector-492513457), [education](https://huggingface.co/HuggingFaceFW/fineweb-edu-classifier) classifications.

## Pre-requisites
Before running this assignment, ensure you have:
- Docker installed on your system
- Docker Desktop installed and running
## Running the Assignment
To run this assignment, follow these steps:
- Open your terminal and navigate to the repository directory.
- Run the following commands:
```Bash
docker-compose build
docker-compose up
```

## Using the Application
Once the application is running, you can access it at:
http://localhost:9876/
Here, you can:
- Input text data (currently the apis are still slow, working on enhancing multi threading)
- View displayed data
- Visualize data through interactive graphs

## For a better understanding, refer to the attached screenshots:
![image](https://github.com/user-attachments/assets/7f24a8f0-0fc4-4085-99f4-3b287f5aa01b)
![image](https://github.com/user-attachments/assets/906caa01-2ce1-4d4d-8898-4f61c25dba6e)


