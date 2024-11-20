import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class ApiService {
  public apiUrl = 'http://127.0.0.1:8000/api/submit_text'; // Update als je backend anders draait

  constructor(private http: HttpClient) {}

  // Functie om de tekst naar de backend te sturen
  submitText(formData: any): Observable<any> {
    return this.http.post<any>(this.apiUrl, formData);
  }

  // AI: Verkrijg suggesties (POST /api/get_suggestions)
  getSuggestions(text: string, text_type: string): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/get_suggestions`, {
      text,
      text_type,
    });
  }

  // Scraper: Verkrijg lijst van items (GET /api/items)
  getItems(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/items`);
  }

  // Scraper: Verkrijg een specifiek item op basis van item_id (GET /api/items/{item_id})
  getItemById(itemId: string): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/items/${itemId}`);
  }

  // Scraper: Maak een nieuw item aan (POST /api/items/{item_id})
  createItem(itemId: string, itemData: any): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/items/${itemId}`, itemData);
  }
}
