import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { AuthService } from '../services/auth.service';

interface RawTextResponse {
  message: string;
  id: string;
  data: any;
}

@Injectable({
  providedIn: 'root',
})
export class ApiService {
  //succes met dit in de env variablen te krijgen
  private baseUrl = 'https://kevinvanrooy.be/api';

  constructor(
    private http: HttpClient,
    private authService: AuthService
  ) {}

  private getHeaders(): HttpHeaders {
    const token = this.authService.getToken();
    return new HttpHeaders({
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    });
  }

  private getFullUrl(endpoint: string): string {
    return `${this.baseUrl}${endpoint}`;
  }

  // POST raw-text
  async postRawText(rawText: string, textType: string): Promise<string> {
    try {
      const response = await firstValueFrom(
        this.http.post<RawTextResponse>(
          this.getFullUrl('/raw_text'),
          {
            text: rawText,
            text_type: textType.toLowerCase()
          },
          { headers: this.getHeaders() }
        )
      );
      console.log('Raw text response:', response);
      return response.id;
    } catch (error) {
      console.error('Error posting raw text:', error);
      throw error;
    }
  }

  // POST suggestion
  async postSuggestion(rawTextId: string): Promise<any> {
    try {
      const response = await firstValueFrom(
        this.http.post(
          this.getFullUrl(`/suggestions/${rawTextId}`),
          {},
          { headers: this.getHeaders() }
        )
      );
      return response;
    } catch (error) {
      console.error('Error posting suggestions:', error);
      throw error;
    }
  }

  // GET suggestion
  async getSuggestion(suggestionId: string): Promise<any> {
    try {
      const response = await firstValueFrom(
        this.http.get(
          this.getFullUrl(`/suggestion/${suggestionId}`),
          { headers: this.getHeaders() }
        )
      );
      console.log('Raw getSuggestions response:', response);
      return response;
    } catch (error) {
      console.error('Error getting suggestions:', error);
      throw error;
    }
  }

  // UPDATE raw-text
  async updateRawText(rawTextId: string, rawText: string, textType: string): Promise<any> {
    try {
      const response = await firstValueFrom(
        this.http.put(
          this.getFullUrl(`/raw_text/${rawTextId}`),
          {
            text: rawText,
            text_type: textType.toLowerCase()
          },
          { headers: this.getHeaders() }
        )
      );
      return response;
    } catch (error) {
      console.error('Error updating raw text:', error);
      throw error;
    }
  }

  // UPDATE suggestion
  async updateSuggestion(suggestionId: string): Promise<any> {
    try {
      const response = await firstValueFrom(
        this.http.put(
          this.getFullUrl(`/suggestions/${suggestionId}`),
          {},
          { headers: this.getHeaders() }
        )
      );
      return response;
    } catch (error) {
      console.error('Error updating suggestions:', error);
      throw error;
    }
  }

  // POST final-text
  async postFinalText(text: string, rawTextId: string, suggestionId: string): Promise<any> {
    try {
      const response = await firstValueFrom(
        this.http.post(
          this.getFullUrl('/final_text'),
          {
            text: text,
            raw_text_id: rawTextId,
            suggestion_id: suggestionId
          },
          { headers: this.getHeaders() }
        )
      );
      return response;
    } catch (error) {
      console.error('Error posting final text:', error);
      throw error;
    }
  }
}
