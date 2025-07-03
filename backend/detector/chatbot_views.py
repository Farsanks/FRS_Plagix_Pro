import os
from dotenv import load_dotenv
from rest_framework.views import APIView
from rest_framework.response import Response
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class ChatbotView(APIView):
    def post(self, request):
        message = request.data.get("message")
        if not message:
            return Response({"error": "Message is required"}, status=400)

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": message}
                ]
            )
            reply = response.choices[0].message.content.strip()
            return Response({"reply": reply})
        except Exception as e:
            return Response({"error": str(e)}, status=500)
