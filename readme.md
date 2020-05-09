# Membership Management Customer Setup
## 1. Stripe account. Get api public key, secret key, webhook endpoint and secret.

## endpoint events needed:
* customer.subscription.deleted
* invoice.payment_succeeded
* checkout.session.completed
* customer.subscription.updated

## 2. postmark domain verification or set up Gmail SMTP and allow less secure apps. Gmail turn on less secure apps: https://support.google.com/accounts/answer/6010255?hl=en or https://support.google.com/a/answer/6260879 
## 3. update site logo
## 4. update company name

### (optional) purchase barcode scanner: https://amzn.to/3edfgVD
### (optional) optional barcode generator link: https://mobiledemand-barcode.azurewebsites.net/barcode/image?content=test@test.com&size=80&symbology=CODE_128&format=png&text=true