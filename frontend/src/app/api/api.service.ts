import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class ApiService {
  public baseUrl = 'http://127.0.0.1:8000/api';

  constructor(private http: HttpClient) {}

  // POST raw-text
  postRawText(input_text: string, input_type: string): Observable<any> {
    return this.http.post(`${this.baseUrl}/llm/raw_text`, {
      input_text,
      input_type,
    });
  }

  // Verkrijg lijst van items (GET /api/items)
  // getItems(): Observable<any> {
  //   return this.http.get<any>(`${this.apiUrl}/items`);
  // }

  // Verkrijg een specifiek item op basis van item_id (GET /api/items/{item_id})
  // getItemById(itemId: string): Observable<any> {
  //   return this.http.get<any>(`${this.apiUrl}/items/${itemId}`);
  // }

  // Maak een nieuw item aan (POST /api/items/{item_id})
  // createItem(itemId: string, itemData: any): Observable<any> {
  //   return this.http.post<any>(`${this.apiUrl}/items/${itemId}`, itemData);
  // }
}
