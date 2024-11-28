import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import axios from 'axios';


@Injectable({
  providedIn: 'root',
})
export class ApiService {
  private baseUrl = 'https://antwerpen.localhost/api';

  constructor() {}

  private getFullUrl(endpoint: string): string {
    return `${this.baseUrl}${endpoint}`;
  }

  // POST raw-text
  async postRawText(rawText: string, textType: string): Promise<any> {
    try {
        const response = await axios.post(this.getFullUrl('/raw_text'), {
            text: rawText,
            text_type: textType.toLowerCase()
        });
        return response.data.id; 
    } catch (error) {
        console.error('Error posting raw text:', error);
        throw error;
    }
  }

  // POST suggestion
  async postSuggestion(rawTextId: string): Promise<any> {
    try {
        const response = await axios.post(this.getFullUrl(`/suggestions/${rawTextId}`));
        return response.data;
    } catch (error) {
        console.error('Error posting suggestions:', error);
        throw error;
    }
  }

  // GET suggestion
  async getSuggestion(suggestionId: string): Promise<any> {
    try {
        const response = await axios.get(this.getFullUrl(`/suggestion/${suggestionId}`));
        console.log('Raw getSuggestions response:', response.data);  // Debug log
        return response.data;
    } catch (error) {
        console.error('Error getting suggestions:', error);
        throw error;
    }
  }

  // UPDATE raw-text
  async updateRawText(rawTextId: string, rawText: string, textType: string): Promise<any> {
    try {
        const response = await axios.put(this.getFullUrl(`/raw_text/${rawTextId}`), {
            text: rawText,
            text_type: textType.toLowerCase()
        });
        return response.data;
    } catch (error) {
        console.error('Error updating raw text:', error);
        throw error;
    }
  }

  // UPDATE suggestion
  async updateSuggestion(suggestionId: string): Promise<any> {
    try {
        const response = await axios.put(this.getFullUrl(`/suggestions/${suggestionId}`));
        return response.data;
    } catch (error) {
        console.error('Error updating suggestions:', error);
        throw error;
    }
  }

  // POST final-text
  async postFinalText(text: string, rawTextId: string, suggestionId: string): Promise<any> {
    try {
      const response = await axios.post(this.getFullUrl('/final_text'), {
        text: text,
        raw_text_id: rawTextId,
        suggestion_id: suggestionId
      });
      return response.data;
    } catch (error) {
      console.error('Error posting final text:', error);
      throw error;
    }
  }
}
