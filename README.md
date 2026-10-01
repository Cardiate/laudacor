<p align="center">
  <img src="./logo.png" alt="LaudaCor API Logo" width="600">
</p>
</p>
</p>

# LAUDACOR API

### CT Imaging API for Cardiovascular Reporting

---

## Introduction

**LaudaCor** is an open-source, interactive imaging API designed to optimize cardiovascular CT angiography reporting and measurements. 

The project standardizes CT interpretation according to the **SCCT 18-segment protocol** and provides structured templates and prompts to reduce repetitive tasks when working with LLM-based tools. 

Our goal is to reduce reporting processing time by **up to 50%**, helping cardiologists streamline their workflow and focus on clinical interpretation.

<br/>

## Live Demos

* **Interactive web service:** [Watch Video Demo on YouTube](https://www.youtube.com/watch?v=7Lf4Co2AwDw)

<br/>

## ✨ Key Features

* 🔓 **Open-access API**
* 🤖 **LLM/AI integration ready**
* 📱 **REST API with flexible endpoints**
* 🫀 **SCCT 18-segment CT representation**
* 📝 **Structured reporting templates and prompts**
* ⚡ **Workflow optimization for cardiovascular CT reporting**

<br/>

## Getting Started

### 1. Web Service
LaudaCor is available as an interactive web service:  
[http://laudacor.imside.com.br/](http://laudacor.imside.com.br/)

### 2. Recommended LLM
We recommend using **Claude (Anthropic)** as the primary LLM for the current workflow.

### 3. Keyboard Shortcuts
Keyboard shortcuts can be used to streamline the reporting process and improve workflow efficiency.

<br/>

## For Software Developers

The responsive SCCT 18-segment image representation was created using contours extracted from a `.png` image with **OpenCV**. 

The contours are simplified using the **Ramer–Douglas–Peucker algorithm** to reduce the number of points while preserving the overall shape.

This process is implemented in the script:
```bash
desenho.py
```
*(Uses `figura.png` as its input file)*

<br/>

## Contributing

Contributions are welcome! To contribute:

1. Clone the repository.
2. Create a separate branch for your changes (`git checkout -b feature/sua-feature`).
3. Implement and test your modifications.
4. Commit your changes (`git commit -m 'Adiciona nova funcionalidade'`).
5. Open a **Pull Request** for review.

<br/>

## License

This project is licensed under the **Apache License 2.0**.
