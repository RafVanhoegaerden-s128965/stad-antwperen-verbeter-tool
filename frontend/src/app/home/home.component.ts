import { Component } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { ApiService } from '../api/api.service';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { AuthService } from '../services/auth.service';

interface Correction {
  incorrect_part: string;
  corrected_part: string;
  explanation: string;
  error_severity: number;
  info: {
    startPos: number;
    endPos: number;
  };
}

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [ReactiveFormsModule, CommonModule],
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css'],
})
export class HomeComponent {
  textForm: FormGroup;
  private currentRawTextId?: string;
  private currentSuggestionId?: string;
  suggestions: Correction[] = [];
  private originalResponseText: string = '';
  isLoading: boolean = false;

  constructor(
    private formBuilder: FormBuilder,
    private apiService: ApiService,
    private authService: AuthService,
    private router: Router
  ) {
    this.textForm = this.formBuilder.group({
      originalText: [''],
      generatedText: [''],
      mediumType: [''],
    });
  }

  async onGeneralize() {
    const originalText = this.textForm.get('originalText')?.value;
    let mediumType = this.textForm.get('mediumType')?.value;

    if (!originalText || !mediumType) {
      console.error('Please fill in both text and medium type');
      return;
    }

    if (mediumType.toLowerCase() === 'artikel') {
      mediumType = 'article';
    }

    try {
      this.isLoading = true;
      this.textForm.patchValue({
        generatedText: '',
      });

      if (this.currentRawTextId && this.currentSuggestionId) {
        console.log('Updating existing text and suggestions...');
        await this.apiService.updateRawText(
          this.currentRawTextId,
          originalText,
          mediumType
        );
        const updatedSuggestions = await this.apiService.getSuggestion(
          this.currentSuggestionId
        );
        this.processSuggestions(updatedSuggestions);
      } else {
        console.log('Creating new text and suggestions...');
        const rawTextId = await this.apiService.postRawText(
          originalText,
          mediumType
        );
        console.log('Raw text response:', rawTextId);
        this.currentRawTextId = rawTextId;

        if (!this.currentRawTextId) {
          throw new Error('Failed to get raw text ID');
        }

        const suggestionResponse = await this.apiService.postSuggestion(
          this.currentRawTextId
        );
        console.log('Suggestion response:', suggestionResponse); // Debug log
        this.currentSuggestionId = suggestionResponse?.id;

        const suggestions = await this.apiService.getSuggestion(
          suggestionResponse.id
        );
        this.processSuggestions(suggestions);
      }
    } catch (error) {
      console.error('Error during text generation:', error);
      this.textForm.patchValue({
        generatedText: 'Error: Failed to process text',
      });
    } finally {
      this.isLoading = false;
    }
  }

  private processSuggestions(response: any) {
    if (response?.suggestions?.corrections) {
      this.suggestions = response.suggestions.corrections;
      this.originalResponseText = response.text;
      this.updateGeneratedText();
    }
  }

  private updateGeneratedText() {
    let currentText = this.originalResponseText;

    // Sort suggestions by their position in descending order to avoid offset issues
    const sortedSuggestions = [...this.suggestions].sort(
      (a, b) => (b.info?.startPos ?? 0) - (a.info?.startPos ?? 0)
    );

    for (const suggestion of sortedSuggestions) {
      const startPos = suggestion.info?.startPos ?? 0;
      const endPos = suggestion.info?.endPos ?? 0;

      // Keep the original text for this suggestion
      const beforeText = currentText.substring(0, startPos);
      const afterText = currentText.substring(endPos);
      currentText = beforeText + suggestion.incorrect_part + afterText;
    }

    this.textForm.patchValue({
      generatedText: currentText,
    });
  }

  acceptSuggestion(index: number) {
    const suggestion = this.suggestions[index];

    // Replace text at the correct position
    const startPos = suggestion.info?.startPos ?? 0;
    const endPos = suggestion.info?.endPos ?? 0;

    const currentText = this.textForm.get('generatedText')?.value;
    const newText =
      currentText.substring(0, startPos) +
      suggestion.corrected_part +
      currentText.substring(endPos);

    // Update original response text for future reference
    this.originalResponseText = newText;

    // Remove the suggestion and update the display
    this.suggestions.splice(index, 1);

    this.textForm.patchValue({
      generatedText: newText,
    });
  }

  rejectSuggestion(index: number) {
    const suggestion = this.suggestions[index];

    // Keep the original text at this position
    const startPos = suggestion.info?.startPos ?? 0;
    const endPos = suggestion.info?.endPos ?? 0;

    const currentText = this.textForm.get('generatedText')?.value;
    const newText =
      currentText.substring(0, startPos) +
      suggestion.incorrect_part +
      currentText.substring(endPos);

    // Update original response text for future reference
    this.originalResponseText = newText;

    // Remove the suggestion
    this.suggestions.splice(index, 1);

    this.textForm.patchValue({
      generatedText: newText,
    });
  }

  async onFinalize() {
    try {
      if (!this.currentRawTextId || !this.currentSuggestionId) {
        console.error('Missing required IDs for finalization');
        return;
      }

      const finalText = this.textForm.get('generatedText')?.value;

      await this.apiService.postFinalText(
        finalText,
        this.currentRawTextId,
        this.currentSuggestionId
      );

      // Reset everything
      this.currentRawTextId = undefined;
      this.currentSuggestionId = undefined;
      this.suggestions = [];
      this.originalResponseText = '';

      // Reset form
      this.textForm.patchValue({
        originalText: '',
        generatedText: '',
        mediumType: '',
      });
    } catch (error) {
      console.error('Error during finalization:', error);
    }
  }

  onLogout(): void {
    this.authService.logout();
    this.router.navigate(['/login']);
  }
}
