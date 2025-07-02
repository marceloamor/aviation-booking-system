# Northeastern Airways Booking System

## Project Overview

This project is part of the **LCSCI7228 – Database Management Systems** course at Northeastern University London.

### Objective
Build a full-stack, database-driven application for **Northeastern Airways**, a airline operating domestic flights. The app enables:

- Passenger registration and flight booking
- Personnel and admin management
- Flight scheduling and aircraft tracking
- Post-flight feedback collection
- SQL-based report generation

This system supports multi-user roles and demonstrates practical database design, normalization, and integration with a web-based frontend.

---

## Functional Modules

### User Management
- Register users with full contact and address details
- Users can have one or more roles: **Passenger**, **Admin**, **Technical Staff**, or **Non-Technical Staff**
- Authentication and role-based access control (admin tasks)

### Flight & Schedule Management
- Technical staff can create flights
- Associate flights with aircraft, add costs, and track schedules
- Return flights and self-referencing scheduling support
- Real-time status updates (e.g., Scheduled, Delayed, Landed)

### Booking System
- Passengers can search for and book flights
- Booking generates confirmation codes and logs costs
- History view for users showing past flights and total spend

### Ratings & Feedback
- Passengers leave 1–5 star ratings after flights
- Optional comments
- Automated thank-you message sent to each passenger

### SQL Reports
The system includes 5 reports built with complex SQL, demonstrating:
- Joins (including non-inner joins)
- Subqueries
- Aggregations
- Grouping & ordering
- Expressions in SELECT/WHERE
- Use of `HAVING` conditions

---

## Database Schema

### Tables & Relationships

#### `User`
- `id` (PK)
- `first_name`, `last_name`
- `email` (unique, login)
- `password_hash`
- `profile_picture` (nullable)
- `phone_number`
- `street`, `city`, `postal_code`, `country`
- `created_at`, `updated_at`

#### `Role`
- `id` (PK)
- `name` (e.g. "passenger", "admin", "technical_staff")

#### `UserRole`
- `user_id` (FK → User.id)
- `role_id` (FK → Role.id)
- **Composite PK**: (`user_id`, `role_id`)

#### `Aircraft`
- `id` (PK)
- `model_number`, `serial_number`, `registration_number`
- `manufacturer`
- `date_of_manufacture`
- `aircraft_class`, `generic_name`, `popular_name`
- `number_of_engines`
- `aip_info` (Text/JSON)

#### `Flight`
- `id` (PK)
- `flight_number`
- `aircraft_id` (FK → Aircraft.id)
- `created_by_user_id` (FK → User.id)
- `base_cost`

#### `FlightSchedule`
- `id` (PK)
- `flight_id` (FK → Flight.id)
- `departure_airport`, `arrival_airport`
- `departure_terminal`, `departure_gate`
- `scheduled_departure_time`, `actual_departure_time`
- `scheduled_arrival_time`, `actual_arrival_time`
- `status` (Scheduled, Landed, Delayed, etc.)
- `flight_plan_notes`, `meals_provided`
- `return_schedule_id` (nullable FK → FlightSchedule.id)

#### `Booking`
- `id` (PK)
- `passenger_id` (FK → User.id)
- `flight_schedule_id` (FK → FlightSchedule.id)
- `booking_date`
- `confirmation_code`
- `cost_charged`
- `thank_you_sent` (Boolean)
- `payment_status`

#### `Rating`
- `id` (PK)
- `booking_id` (FK → Booking.id)
- `stars` (1–5)
- `comments`
- `created_at`

---

## Tech Stack

| Layer         | Technology      |
|---------------|-----------------|
| **Frontend**  | Python + Dash |
| **Backend**   | Python + Dash callbacks |
| **Database**  | SQLite (via SQLAlchemy ORM) |
| **ORM**       | SQLAlchemy |
| **Versioning**| Git + GitHub |
| **IDE**       | Cursor |
| **Deployment**| Local dev |

### Why Dash?
- Simplified integration of Python + UI
- Rapid prototyping for dashboards/forms
- Built-in support for interactive components

### Why SQLAlchemy + SQLite?
- SQLAlchemy allows DB-agnostic ORM design
- SQLite is easy to set up locally
- Future-proofing: can switch to PostgreSQL with minimal code changes

