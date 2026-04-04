import os
import django
import pandas as pd

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "safe.settings")
django.setup()

from core.models import HealthProfile

data = []

for p in HealthProfile.objects.all():
    data.append({
        "age": p.age,
        "height": p.height,
        "weight": p.weight,
        "bmi": p.bmi,
        "symptoms": p.symptoms,
        "heart_history": p.heart_history,
        "severity": p.severity
    })

df = pd.DataFrame(data)
df.to_csv("safe_dataset.csv", index=False)

print("Dataset exported successfully")





































































































