## UPS Integration for ERPNext

This Frappe app is designed to integrate UPS (United Parcel Service) functionalities into ERPNext.

*Note: This project is a work in progress. The documentation and code are provided as-is, and further development may be needed to suit your specific requirements.*

### Prerequisites

Before you begin, ensure you have the following:

1. **UPS Account**: An account with UPS is required. Sign up or log in at [ups.com](https://www.ups.com/).

2. **Account Number**: Obtain an account number from UPS, essential for transactions.

3. **Developer Account on UPS**: Log in to the UPS Developer Portal ([developer.ups.com](https://developer.ups.com/)) for API access.

4. **App Registration**: Create an application via the UPS Developer Portal for integrating UPS technology into your ERPNext. Use the *Client Credentials Grant Type*. Select `I want to integrate UPS technology into my business` during creation.

5. **API Subscriptions**: Include the following products/APIs in your application:
    - Authorization (OAuth)
    - Shipping

### Project Overview

This app facilitates seamless integration with UPS services, including shipping, tracking, and address validation, within ERPNext.

### Key Components

1. **UPS Client (`ups_client.py`)**: 
   - Manages API requests to UPS.
   - Handles session management, token generation, and authorization.
   - Includes methods for session creation and closure, token fetching and setting, and making generic UPS API requests.

2. **UPS Shipment Doctype (`ups_shipment`)**: 
   - Defines the structure for shipment records.
   - Contains logic for preparing and sending shipment requests to UPS, and handling responses including tracking numbers and label generation.

3. **UPS Settings Doctype (`ups_settings`)**: 
   - Stores UPS account settings and credentials.
   - Provides functions for retrieving the API base URL, bearer token, client ID, and client secret.
   - Manages access token expiration and renewal.

4. **Additional Doctypes**: 
   - `UPS Shipment Package` and `UPS Shipment Charge` for structuring packages and charges related to a shipment.

### Installation

1. Clone the repository into your bench apps folder: `bench get-app https://github.com/alyf-de/ups_integration.git`.
2. Install the app: `bench install-app ups_integration`.
3. Configure the UPS Settings in ERPNext with the necessary credentials and preferences.

### Usage

1. Set up UPS Settings with your UPS account details, including API credentials.
2. Create a UPS Shipment document in ERPNext, filling in details like shipper, recipient, and package information.
3. On saving or submitting the shipment, the app communicates with UPS to create the shipment and fetch tracking details.

### Development

Key areas for improvement include:

- Expanding the `UPSClient` class to cover more UPS API endpoints.
- Enhancing the `UPS Shipment` Doctype with features like real-time tracking updates.
- Customizing the user interface and workflow to better fit specific business processes.

### License

GPL-3.0
