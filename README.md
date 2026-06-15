# AI Code Critic Microservice

This repository contains the Python AI microservice for the Code Critic application. It serves as the intelligence layer in a three-tier architecture, receiving code from a Java Spring Boot backend, analyzing it using the Google Gemini API, and returning structured feedback.

## 🚀 Architecture Overview

This service is built with **FastAPI** and **Uvicorn**, designed to run as a standalone private service on Render.
* **Frontend:** React
* **Backend:** Java Spring Boot
* **AI Engine (This Repo):** Python FastAPI + Google Gemini 2.5 Flash

## ⚙️ Prerequisites & Setup

To run this microservice locally, you need Python 3 installed.

1. **Clone the repository and navigate to the directory:**
   ```bash
   git clone <your-repo-url>
   cd <your-repo-name>
