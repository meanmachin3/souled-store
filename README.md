# souled-store

An endpoint receives Email HTML content and Email Address, The application sends this email through a celery task.

* **URL**

  /v1/mail/send

* **Method:**
  
  `POST`
  
*  **URL Params**

   **Required:**
 
   `cc=[array]`
   `content = [array]`

   **Optional:**
 
   `subject = [string]`

* **Data Params**

  `{
	"to": [
		"missinghome@mailinator.com",
		"hello@mailinator.com"
	],
	"subject": "Hello World!",
	"content": [{
		"type": "text/plain",
		"value": "Heyya!!"
	},{
		"type": "text/html",
		"value": "<h1> Hello World! </h1>"
	}]
}`

* **Success Response:**

  * **Code:** 200 <br />
    **Content:** `{"message":"Successfully Queued","status":200}`
 
* **Error Response:**

  * **Code:** 400 BAD REQUEST <br />
    **Content:** `{"message": "Invalid content field", "status": 400}`

  * **Code:** 415 UNSUPPORTED TYPE <br />
    **Content:** `"message": "Unsupported Media Type ;)", "status": 415}`
  
  * **Code:** 415 UNSUPPORTED TYPE <br />
    **Content:** `"message": "Unsupported Media Type ;)", "status": 415}`

* **Sample Call:**

  ```
  curl -X POST \
  https://souled-store.herokuapp.com/v1/mail/send \
  -H 'Cache-Control: no-cache' \
  -H 'Content-Type: application/json' \
  -d '{
	"to": [
		"missinghome@mailinator.com",
		"hello@mailinator.com"
	],
	"subject": "Hello World!",
	"content": [{
		"type": "text/plain",
		"value": "Heyya!!"
	},{
		"type": "text/html",
		"value": "<h1> Hello World! </h1>"
	}]
  }'
  ```
