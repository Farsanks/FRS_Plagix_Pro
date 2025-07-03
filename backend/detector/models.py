from django.db import models

class Document(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='documents/')
    content = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class ComparisonHistory(models.Model):
    doc1 = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='comparisons_as_doc1')
    doc2 = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='comparisons_as_doc2')
    plagiarism_percentage = models.FloatField()
    # New field to store the list of matched sentences (as JSON)
    match_details = models.JSONField(blank=True, null=True)
    compared_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.doc1} vs {self.doc2} at {self.compared_at}"
