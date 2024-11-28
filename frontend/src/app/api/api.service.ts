import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class ApiService {
  private baseUrl = 'https://antwerpen.localhost/api';

  constructor(private http: HttpClient) { }

  private getFullUrl(endpoint: string): string {
    return `${this.baseUrl}${endpoint}`;
  }

  // POST raw-text
  async postRawText(rawText: string, textType: string): Promise<any> {
    try {
      const response = await firstValueFrom(
        this.http.post(this.getFullUrl('/raw_text'), {
          text: rawText,
          text_type: textType.toLowerCase()
        })
      );
      return response;
    } catch (error) {
      console.error('Error posting raw text:', error);
      throw error;
    }
  }

  // POST suggestion
  async postSuggestion(rawTextId: string): Promise<any> {
    try {
      const response = await firstValueFrom(
        this.http.post(this.getFullUrl(`/suggestions/${rawTextId}`), {})
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
        this.http.get(this.getFullUrl(`/suggestion/${suggestionId}`))
      );
      console.log('Raw getSuggestions response:', response);  // Debug log
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
        this.http.put(this.getFullUrl(`/raw_text/${rawTextId}`), {
          text: rawText,
          text_type: textType.toLowerCase()
        })
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
        this.http.put(this.getFullUrl(`/suggestions/${suggestionId}`), {})
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
        this.http.post(this.getFullUrl('/final_text'), {
          text: text,
          raw_text_id: rawTextId,
          suggestion_id: suggestionId
        })
      );
      return response;
    } catch (error) {
      console.error('Error posting final text:', error);
      throw error;
    }
  }
}
