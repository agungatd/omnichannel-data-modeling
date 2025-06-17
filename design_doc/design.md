# Design Document: ShopSphere Omnichannel Data Platform

## Introduction and Goals

The primary goal is to build "single source of truth" that is reliable, scalable, and serve multiple use cases:

1. **Business Analytics and Customer 360**: Provide holistic view of customers and their interactions accross all channels.
2. **Real-time Inventory Tracking**: Maintain accurate, near real-time stock levels.
3. **Fraud Detection**: Identify and flag suspicious activities in real-time, probably feeding cleaned and transformed data into a Machine Learning model for fraud detection.

After this we will refer to each use case with its order number (e.g. for Fraud Detection use `case no.3`).

##