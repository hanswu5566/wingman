
class UserAction:
    SIGN_UP = 'sign_up'
    SETUP= 'setup'



ONBOARDING_MSG = {
	"blocks": [
		{
			"type": "header",
			"text": {
				"type": "plain_text",
				"text": "Welcome to Wingman! 🎉"
			}
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "Hello and welcome to Wingman! We are thrilled to have you join us. \nWingman is an AI assistant designed to elevate your productivity by leveraging Large Language Models (LLM) to seamlessly integrate with project management software and streamline your daily task management.\n"
			}
		},
	]
}

SIGNUP_SUCCEED_MSG={
    "blocks":[
        
	]
}


SETUP_MSG ={
    "blocks":[
        {
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": " We noticed that you've interacted with the bot.\n We exclusively support Clickup now. Asana and Monday will be coming soon.\nPlease configure your preferred management tool first to enable the service."
			}
		},
		{
			"type": "actions",
			"elements": [
				{
					"type": "static_select",
					"placeholder": {
						"type": "plain_text",
						"text": "Setup management tool"
					},
					"action_id": UserAction.SETUP,
					"options": [
						{
							"text": {
								"type": "plain_text",
								"text": "ClickUp"
							},
							
							"value": "clickup"
						}
					]
				}
			]
		}
	]
}