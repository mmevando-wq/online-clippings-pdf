# Online Clippings PDF

Flask app που δέχεται URL άρθρου, ανακτά τίτλο/συντάκτη/ημερομηνία/κείμενο και δημιουργεί PDF A4 με Arial 11.

## Τοπική εκτέλεση με Docker

```bash
docker build -t clippings .
docker run -p 10000:10000 clippings
```

Άνοιξε http://localhost:10000

## Render
Ανέβασε τα αρχεία σε GitHub και δημιούργησε νέο Blueprint στο Render από το `render.yaml`.

## Περιορισμοί
Paywalls, login, robots/anti-bot και client-side rendering μπορεί να εμποδίσουν την πλήρη ανάκτηση. Το UI επιτρέπει χειροκίνητη διόρθωση πριν τη δημιουργία PDF.
