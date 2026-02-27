from django.db import IntegrityError
import jellyfish
from django.shortcuts import render
from .models import NewspaperTitle
from rapidfuzz import fuzz, process

def title_checker(request):
    PROHIBITED = ['POLICE', 'CBI', 'CID', 'ARMY', 'GOVERNMENT', 'MODI', 'STATE']
    IGNORE = ['THE', 'DAILY', 'WEEKLY', 'MONTHLY', 'NEWSPAPER']
    
    if request.method == "POST":
        # 1. Capture both potential inputs
        single_input = request.POST.get('title', '').strip()
        bulk_input = request.POST.get('multiple', '').strip()

        # 2. Combine into a list of titles to process
        titles_to_process = []
        if single_input:
            titles_to_process.append(single_input)
        if bulk_input:
            # Splits by new line and cleans up whitespace
            titles_to_process.extend([t.strip() for t in bulk_input.splitlines() if t.strip()])

        if not titles_to_process:
            return render(request, 'index.html', {'error': 'Please enter at least one title.'})

        final_results = []
        
        # 3. Pre-fetch titles for better performance (Requirement 5c)
        # We fetch the full list once per request instead of inside the loop
        all_db_titles = list(NewspaperTitle.objects.values_list('title_text', flat=True))

        for original_title in titles_to_process:
            upper_title = original_title.upper()
            title_words = upper_title.split()

            # Rule: Prohibited Words
            if any(word in title_words for word in PROHIBITED):
                final_results.append({
                    'user_title': original_title,
                    'status': '✖️Rejected',
                    'probability': 0,
                    'reason': 'Contains Prohibited Word (Legal Violation)'
                })
                continue

            # NLP: Clean Title
            cleaned_title = " ".join([w for w in title_words if w not in IGNORE])
            if not cleaned_title:
                final_results.append({
                    'user_title': original_title,
                    'status': '✖️Rejected',
                    'probability': 0,
                    'reason': 'Title is too generic after removing common words.'
                })
                continue

            # 4. Matching Logic (Requirement 1 & 3)
            # Using token_sort_ratio as you correctly identified
            match = process.extractOne(cleaned_title, all_db_titles, scorer=fuzz.token_sort_ratio)
            
            status = "✔️Approved"
            reason = "Unique and compliant."
            prob = 100
            match_name = None

            if match:
                match_name, score, _ = match
                user_sound = jellyfish.metaphone(cleaned_title)
                match_sound = jellyfish.metaphone(match_name)
                phonetic_match = (user_sound == match_sound)
                
                prob = round(100 - score, 2)

                if score > 75 or phonetic_match:
                    status = "✖️Rejected"
                    reason = f"Sounds identical to '{match_name}'." if phonetic_match else f"Too similar to '{match_name}'."
                elif score > 50:
                    status = "Warning"
                    reason = f"Moderate similarity to '{match_name}'. Review recommended."
            if status == "✔️Approved":
                try:
                    # Save to DB so the NEXT search sees this title as "existing"
                    NewspaperTitle.objects.get_or_create(title_text=upper_title)
                except IntegrityError:
                    # If it's already there, we just ignore the error
                    pass

            final_results.append({
                'user_title': original_title,
                'match_name': match_name,
                'probability': prob,
                'status': status,
                'reason': reason
            })

        # Return the list of results to result.html
        return render(request, 'result.html', {
    'results': final_results,
    'approved': sum(1 for r in final_results if '✔' in r['status']),
    'rejected': sum(1 for r in final_results if '✖' in r['status']),
    'warnings': sum(1 for r in final_results if r['status'] == 'Warning'),
})

    return render(request, 'index.html')