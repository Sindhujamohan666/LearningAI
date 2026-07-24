# ShopStream SRS - Software Requirements Specification

## Introduction
ShopStream is a modern e-commerce platform designed for scalability and user experience.

## Functional Requirements

FR-001: The system shall allow users to register using email/password combination
FR-002: The system shall support OAuth 2.0 social login (Google, Facebook)
FR-003: The system shall enforce password complexity (min 8 chars, 1 uppercase, 1 number, 1 special char)
FR-004: The system shall send verification email after registration
FR-005: The system shall lock account after 5 consecutive failed login attempts
FR-006: The system shall display product catalog with image gallery
FR-007: The system shall support faceted search with filters
FR-008: The system shall maintain shopping cart state for 30 days for authenticated users
FR-009: The system shall calculate tax based on shipping address
FR-010: The system shall process payments through Stripe integration
FR-011: The system shall generate order confirmation PDF
FR-012: The system shall send transactional emails (order confirmation, shipping, delivery)

## Integration Points
- Stripe Payment Gateway v2023-01
- SendGrid for transactional emails
- Google Maps API for address validation
- Twilio for SMS notifications

## Data Models

### User
- id: UUID
- email: string (unique)
- password_hash: string
- mfa_enabled: boolean
- created_at: timestamp
- last_login: timestamp

### Product
- id: UUID
- name: string
- description: text
- price: decimal(10,2)
- stock_quantity: integer
- category_id: UUID
- images: array[string]
- is_active: boolean

### Order
- id: UUID
- user_id: UUID
- status: enum(pending, confirmed, shipped, delivered, cancelled, refunded)
- total_amount: decimal(10,2)
- shipping_address: json
- payment_id: string
- created_at: timestamp
