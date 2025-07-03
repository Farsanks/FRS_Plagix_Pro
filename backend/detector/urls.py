from django.urls import path
from .views import (
    DocumentUploadView,
    PlagiarismCheckView,
    DocumentListView,
    ComparisonHistoryView,
    signup,
    login_user
)
from .chatbot_views import ChatbotView  # ✅ remove ChatbotPageView

urlpatterns = [
    # 📁 Document APIs
    path('upload/', DocumentUploadView.as_view(), name='upload-document'),
    path('compare/', PlagiarismCheckView.as_view(), name='compare-documents'),
    path('documents/', DocumentListView.as_view(), name='document-list'),
    path('history/', ComparisonHistoryView.as_view(), name='comparison-history'),

    # 🔐 Authentication APIs
    path('signup/', signup, name='signup'),
    path('login/', login_user, name='login'),

    # 🤖 Chatbot API only
    path("chat/message/", ChatbotView.as_view(), name="chatbot_api"),  # ✅ change to this
]
