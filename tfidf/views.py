import math
from collections import Counter
from django.shortcuts import render
from django.core.files.storage import default_storage
from django.conf import settings
import os


def compute_tf(text):
    words = text.split()
    total_words = len(words)
    word_counts = Counter(words)
    return {word: count / total_words for word, count in word_counts.items()}, word_counts


def compute_idf(word_counts_list):
    num_docs = len(word_counts_list)
    word_doc_counts = Counter()

    for word_counts in word_counts_list:
        for word in word_counts:
            word_doc_counts[word] += 1

    return {word: math.log(num_docs / count) for word, count in word_doc_counts.items()}


def upload_file(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        if file.name.endswith('.txt'):
            file_path = default_storage.save(f'uploads/{file.name}', file)
            full_path = os.path.join(settings.MEDIA_ROOT, file_path)

            with open(full_path, 'r', encoding='utf-8') as f:
                text = f.read().lower()

            tf_values, word_counts = compute_tf(text)
            idf_values = compute_idf([word_counts])

            results = [(word, word_counts[word], tf_values[word], idf_values[word]) for word in word_counts]
            results = sorted(results, key=lambda x: x[3], reverse=True)[:50]

            return render(request, 'index.html', {'results': results})

    return render(request, 'index.html', {'results': None})
