# Models

This folder is reserved for AI/ML model files used by the
AI Traffic Enforcement system.

## Current Implementation

The current version uses a remote vision-language model through the
Groq API for traffic violation and number plate detection.

The model is configured in the `.env` file:

```env
MODEL_NAME=qwen/qwen3.8-27b