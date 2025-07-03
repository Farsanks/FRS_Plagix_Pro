from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.generics import ListAPIView
from rest_framework import status, serializers
from rest_framework.decorators import api_view
from rest_framework.authtoken.models import Token

from django.utils.timezone import localtime
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate

from .models import Document, ComparisonHistory
from .utils import extract_text_from_file

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from difflib import SequenceMatcher
from nltk.tokenize import sent_tokenize
import nltk

# Ensure nltk punkt is available
nltk.download('punkt')


# 🚀 Document Upload API
class DocumentUploadView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        title = request.data.get('title')
        file = request.data.get('file')

        if not file:
            return Response({'error': 'File is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            content = extract_text_from_file(file)
        except Exception as e:
            return Response({'error': f'Text extraction failed: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

        if not content:
            return Response({'error': 'No text could be extracted from the file'}, status=status.HTTP_400_BAD_REQUEST)

        doc = Document.objects.create(title=title, file=file, content=content)

        return Response({
            'message': 'Uploaded successfully',
            'doc_id': doc.id,
            'content_preview': content[:500]
        }, status=status.HTTP_200_OK)


# 🔍 Document Comparison API
class PlagiarismCheckView(APIView):
    def post(self, request, *args, **kwargs):
        doc1_id = request.data.get('doc1_id')
        doc2_id = request.data.get('doc2_id')

        if not doc1_id or not doc2_id:
            return Response({'error': 'Both document IDs are required'}, status=400)

        try:
            doc1 = Document.objects.get(id=doc1_id)
            doc2 = Document.objects.get(id=doc2_id)
        except Document.DoesNotExist:
            return Response({'error': 'One or both documents not found'}, status=404)

        texts = [doc1.content, doc2.content]
        tfidf = TfidfVectorizer().fit_transform(texts)
        similarity_score = float(cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]) * 100
        plagiarism_percentage = round(similarity_score, 2)

        # Match sentences using difflib
        doc1_sents = sent_tokenize(doc1.content)
        doc2_sents = sent_tokenize(doc2.content)
        matched_sentences = []

        for s1 in doc1_sents:
            for s2 in doc2_sents:
                ratio = SequenceMatcher(None, s1.strip(), s2.strip()).ratio()
                if ratio > 0.8:
                    matched_sentences.append({
                        'doc1_sentence': s1,
                        'doc2_sentence': s2,
                        'match_score': round(ratio * 100, 2)
                    })

        # Save comparison result
        ComparisonHistory.objects.create(
            doc1=doc1,
            doc2=doc2,
            plagiarism_percentage=plagiarism_percentage,
            match_details=matched_sentences
        )

        return Response({
            'doc1_id': doc1.id,
            'doc2_id': doc2.id,
            'plagiarism_percentage': plagiarism_percentage,
            'matches': matched_sentences
        })


# 📄 Document List API
class DocumentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'title']


class DocumentListView(ListAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentListSerializer


# 📊 Comparison History API
class ComparisonHistoryView(APIView):
    def get(self, request):
        history = ComparisonHistory.objects.all().order_by('-compared_at')
        data = [
            {
                "doc1": item.doc1.title,
                "doc2": item.doc2.title,
                "percentage": item.plagiarism_percentage,
                "timestamp": localtime(item.compared_at).strftime("%Y-%m-%d %H:%M"),
                "match_details": item.match_details  # frontend uses this
            }
            for item in history
        ]
        return Response(data)


# 🔐 Signup API
@api_view(['POST'])
def signup(request):
    username = request.data.get('username')
    password = request.data.get('password')
    role = request.data.get('role')
    subject = request.data.get('subject')  # Should be 'Teacher' or 'Student'

    if not username or not password or not role:
        return Response({'error': 'Username, password and role are required'}, status=400)

    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username already exists'}, status=400)

    user = User.objects.create_user(username=username, password=password)

    # Assign group by role
    group, _ = Group.objects.get_or_create(name=role.capitalize())
    user.groups.add(group)

    token, _ = Token.objects.get_or_create(user=user)

    return Response({
        'message': 'Signup successful',
        'token': token.key,
        'username': user.username,
        'role': role
    })


# 🔑 Login API
@api_view(['POST'])
def login_user(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)
    if not user:
        return Response({'error': 'Invalid credentials'}, status=401)

    token, _ = Token.objects.get_or_create(user=user)

    # Determine role from group
    role = 'Student'
    if user.groups.filter(name='Teacher').exists():
        role = 'Teacher'

    return Response({
        'message': 'Login successful',
        'token': token.key,
        'username': user.username,
        'role': role
    })
