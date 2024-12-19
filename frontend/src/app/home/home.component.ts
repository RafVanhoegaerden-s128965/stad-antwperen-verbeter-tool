import { Component, ElementRef, ViewChild, ViewEncapsulation } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { ApiService } from '../api/api.service';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { AuthService } from '../services/auth.service';

interface Correction {
  id?: string;
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
  encapsulation: ViewEncapsulation.None
})

export class HomeComponent {
  textForm: FormGroup;
  private currentRawTextId?: string;
  private currentSuggestionId?: string;
  suggestions: Correction[] = [];
  private originalResponseText: string = '';
  isLoading: boolean = false;

  private lastChangePosition: { start: number, end: number } | null = null;

  tooltipVisible = false;
  tooltipX = 0;
  tooltipY = 0;
  currentTooltipSuggestion: Correction | null = null;
  currentTooltipSuggestions: Correction[] = [];

  private _textInput: string = '';
  get textInput() {
    return this._textInput;
  }
  set textInput(text) {
    this._textInput = text;
    localStorage.setItem('textInput', text);
  }

  constructor(
    private formBuilder: FormBuilder,
    private apiService: ApiService,
    private authService: AuthService,
    private router: Router
  ) {
    this.textForm = this.formBuilder.group({
      inputText: [''],
      outputText: [''],
      mediumType: [''],
    });
    let text = localStorage.getItem('textInput');
    if (text != null) {
      this.textInput = text;
    }
  }

  async onGenerate() {
    const inputText = this.textForm.get('inputText')?.value;
    let mediumType = this.textForm.get('mediumType')?.value;

    if (!inputText || !mediumType) {
      console.error('Please fill in both text and medium type');
      return;
    }

    if (mediumType.toLowerCase() === 'artikel') {
      mediumType = 'article';
    }

    try {
      this.textForm.patchValue({
        generatedText: '',
      });
      this.isLoading = true;

      const rawTextId = await this.apiService.postRawText(inputText, mediumType);
      this.currentRawTextId = rawTextId;

      if (!this.currentRawTextId) {
        throw new Error('Failed to get raw text ID');
      }

      const suggestionResponse = await this.apiService.postSuggestion(this.currentRawTextId);
      this.currentSuggestionId = suggestionResponse?.id;

      const suggestions = await this.apiService.getSuggestion(suggestionResponse.id);
      this.processSuggestions(suggestions);

    } catch (error) {
      console.error('Error during text generation:', error);
      this.generatedTextDiv.nativeElement.innerText = 'Error: Failed to process text';
    } finally {
      this.isLoading = false;
    }
  }

  private processSuggestions(response: any) {
    if (response?.suggestions?.corrections) {
      // Assign unique IDs to suggestions if they don't have one
      this.suggestions = response.suggestions.corrections.map((c: Correction, index: number) => {
        if (!c.id) {
          c.id = `${Date.now()}-${index}`;
        }
        return c;
      });

      this.originalResponseText = response.text;
      this.renderHighlightedText();
    }
  }

  tooltipHideTimeout: any = null;


  private showTooltipForMultiple(event: Event, suggestions: Correction[]) {
    this.currentTooltipSuggestions = suggestions;

    const target = event.target as HTMLElement;
    const rect = target.getBoundingClientRect();

    this.tooltipX = rect.left;
    this.tooltipY = rect.bottom + window.scrollY;
    this.tooltipVisible = true;

    if (this.tooltipHideTimeout) {
      clearTimeout(this.tooltipHideTimeout);
      this.tooltipHideTimeout = null;
    }
  }

  private onHighlightMouseLeave(event: Event) {
    // Start a timeout before hiding tooltip, so user can move into the tooltip
    if (this.tooltipHideTimeout) {
      clearTimeout(this.tooltipHideTimeout);
    }
    this.tooltipHideTimeout = setTimeout(() => {
      this.hideTooltip();
    }, 300);
  }

  showTooltip(event: Event, suggestionId: string) {
    const suggestion = this.suggestions.find(s => s.id === suggestionId);
    if (!suggestion) return;

    this.currentTooltipSuggestion = suggestion;
    const target = event.target as HTMLElement;
    const rect = target.getBoundingClientRect();

    this.tooltipX = rect.left;
    this.tooltipY = rect.bottom + window.scrollY;
    this.tooltipVisible = true;

    // Clear any existing hide timeout if user re-enters the highlight
    if (this.tooltipHideTimeout) {
      clearTimeout(this.tooltipHideTimeout);
      this.tooltipHideTimeout = null;
    }
  }

  acceptSuggestionById(suggestionId?: string) {
    if (!suggestionId) return;
    const index = this.suggestions.findIndex(s => s.id === suggestionId);
    if (index >= 0) {
      this.acceptSuggestion(index);
      this.hideTooltip();
    }
  }

  rejectSuggestionById(suggestionId?: string) {
    if (!suggestionId) return;
    const index = this.suggestions.findIndex(s => s.id === suggestionId);
    if (index >= 0) {
      this.rejectSuggestion(index);
      this.hideTooltip();
    }
  }


  // Hide tooltip after acceptance/rejection
  hideTooltip() {
    this.tooltipVisible = false;
    this.currentTooltipSuggestion = null;
    this.currentTooltipSuggestions = [];
  }

  onSave() {
    if (!this.currentRawTextId || !this.currentSuggestionId) {
      console.error('Missing required IDs for finalization');
      return;
    }

    // Get final text from generatedTextDiv
    const finalText = this.generatedTextDiv.nativeElement.innerText;

    this.apiService.postFinalText(finalText, this.currentRawTextId, this.currentSuggestionId)
      .then(() => {
        // Reset everything
        this.currentRawTextId = undefined;
        this.currentSuggestionId = undefined;
        this.suggestions = [];
        this.originalResponseText = '';

        // Reset form
        this.textForm.patchValue({
          inputText: '',
          outputText: '',
          mediumType: '',
        });

        this.generatedTextDiv.nativeElement.innerText = '';
      })
      .catch(error => {
        console.error('Error during finalization:', error);
      });
  }

  onTooltipMouseEnter() {
    // If the user hovers on the tooltip, clear the hide timeout
    if (this.tooltipHideTimeout) {
      clearTimeout(this.tooltipHideTimeout);
      this.tooltipHideTimeout = null;
    }
  }

  onTooltipMouseLeave() {
    // If user leaves tooltip, hide it immediately or after a short delay
    this.hideTooltip();
  }

  private acceptSuggestion(index: number) {
    const suggestion = this.suggestions[index];
    const startPos = suggestion.info.startPos;
    const endPos = suggestion.info.endPos;

    const currentText = this.originalResponseText;
    const newText =
      currentText.substring(0, startPos) +
      suggestion.corrected_part +
      currentText.substring(endPos);

    this.originalResponseText = newText;

    // Remove the accepted suggestion
    this.suggestions.splice(index, 1);

    const correctedPartLength = suggestion.corrected_part.length;
    const originalPartLength = suggestion.incorrect_part.length;
    const offsetDifference = correctedPartLength - originalPartLength;

    // Remove overlapping suggestions
    this.suggestions = this.suggestions.filter((currentSuggestion) => {
      const cStart = currentSuggestion.info.startPos;
      const cEnd = currentSuggestion.info.endPos;
      const isOverlapping =
        (cStart >= startPos && cStart < endPos) ||
        (cEnd > startPos && cEnd <= endPos) ||
        (cStart <= startPos && cEnd >= endPos);

      return !isOverlapping;
    });

    // Shift subsequent suggestions
    for (const currentSuggestion of this.suggestions) {
      if (currentSuggestion.info.startPos > startPos) {
        currentSuggestion.info.startPos += offsetDifference;
        currentSuggestion.info.endPos += offsetDifference;
      }
    }

    this.renderHighlightedText();
  }

  private rejectSuggestion(index: number) {
    this.suggestions.splice(index, 1);
    this.renderHighlightedText();
  }

  // Nieuw
  onGeneratedTextChange(event: Event) {
    const div = this.generatedTextDiv.nativeElement;
    const newText = div.innerText; // current displayed text after user edit
    const oldText = this.originalResponseText;

    if (newText === oldText) return;

    // Save current selection before modifications
    const selection = document.getSelection();
    const savedRange = this.saveSelection(div);

    // Find changed region
    let start = 0;
    while (start < newText.length && start < oldText.length && newText[start] === oldText[start]) {
      start++;
    }

    let endOld = oldText.length - 1;
    let endNew = newText.length - 1;
    while (endOld >= 0 && endNew >= 0 && oldText[endOld] === newText[endNew] && endOld >= start && endNew >= start) {
      endOld--;
      endNew--;
    }

    const removedLength = (endOld >= start) ? (endOld - start + 1) : 0;
    const addedLength = (endNew >= start) ? (endNew - start + 1) : 0;
    const offsetDifference = addedLength - removedLength;

    this.originalResponseText = newText;

    const changeStart = start;
    const changeEnd = start + Math.max(removedLength, addedLength);

    // Remove overlapping suggestions
    this.suggestions = this.suggestions.filter(suggestion => {
      const sStart = suggestion.info.startPos;
      const sEnd = suggestion.info.endPos;
      const overlaps = !(sEnd <= changeStart || sStart >= changeEnd);
      return !overlaps;
    });

    // Shift subsequent suggestions
    for (const suggestion of this.suggestions) {
      if (suggestion.info.startPos >= changeEnd) {
        suggestion.info.startPos += offsetDifference;
        suggestion.info.endPos += offsetDifference;
      }
    }

    this.renderHighlightedText();

    // Restore selection after re-rendering
    this.restoreSelection(div, savedRange);
  }

  private renderHighlightedText() {
    const div = this.generatedTextDiv.nativeElement;

    // Attempt to preserve caret: save selection
    const savedRange = this.saveSelection(div);

    div.innerHTML = ''; // Clear existing content

    const text = this.originalResponseText;

    if (this.suggestions.length === 0) {
      div.appendChild(document.createTextNode(text));
      // Restore selection after rendering
      this.restoreSelection(div, savedRange);
      return;
    }

    let intervals = this.suggestions.map(s => ({
      start: s.info.startPos,
      end: s.info.endPos,
      suggestions: [s]
    }));

    intervals.sort((a, b) => (a.start !== b.start) ? a.start - b.start : a.end - b.end);

    // Merge overlapping intervals
    const merged: { start: number, end: number, suggestions: Correction[] }[] = [];
    let current = intervals[0];
    for (let i = 1; i < intervals.length; i++) {
      const next = intervals[i];
      if (next.start <= current.end) {
        current.end = Math.max(current.end, next.end);
        current.suggestions.push(...next.suggestions);
      } else {
        merged.push(current);
        current = next;
      }
    }
    merged.push(current);

    let currentIndex = 0;
    for (const interval of merged) {
      const { start, end, suggestions } = interval;
      // Text before highlight
      if (currentIndex < start) {
        div.appendChild(document.createTextNode(text.substring(currentIndex, start)));
      }

      // Highlighted range
      const span = document.createElement('span');
      span.classList.add('highlight-suggestion');
      span.textContent = text.substring(start, end);

      const mouseEnterListener = (event: Event) => this.showTooltipForMultiple(event, suggestions);
      const mouseLeaveListener = (event: Event) => this.onHighlightMouseLeave(event);
      span.addEventListener('mouseenter', mouseEnterListener);
      span.addEventListener('mouseleave', mouseLeaveListener);
      (span as any)._mouseenter = mouseEnterListener;
      (span as any)._mouseleave = mouseLeaveListener;

      div.appendChild(span);
      currentIndex = end;
    }

    // Remaining text
    if (currentIndex < text.length) {
      div.appendChild(document.createTextNode(text.substring(currentIndex)));
    }

    // Restore selection after rendering
    this.restoreSelection(div, savedRange);
  }

  // Utility to save current selection relative to the root element
  private saveSelection(containerEl: HTMLElement): { start: number, end: number } | null {
    const sel = window.getSelection();
    if (!sel || sel.rangeCount === 0) {
      return null;
    }
    const range = sel.getRangeAt(0);

    // We need a way to represent the offset in text nodes relative to containerEl
    const preCaretRange = range.cloneRange();
    preCaretRange.selectNodeContents(containerEl);
    preCaretRange.setEnd(range.startContainer, range.startOffset);
    const start = preCaretRange.toString().length;

    const preCaretRangeEnd = range.cloneRange();
    preCaretRangeEnd.selectNodeContents(containerEl);
    preCaretRangeEnd.setEnd(range.endContainer, range.endOffset);
    const end = preCaretRangeEnd.toString().length;

    return { start, end };
  }

  // Utility to restore selection given start/end offsets
  private restoreSelection(containerEl: HTMLElement, saved: { start: number, end: number } | null) {
    if (!saved) return;
    const { start, end } = saved;
    const charIndex = { index: 0 };

    const range = document.createRange();
    range.setStart(containerEl, 0);
    range.collapse(true);

    const nodeStack: ChildNode[] = Array.from(containerEl.childNodes);
    let node: ChildNode | undefined;

    let foundStart = false;
    let stop = false;

    while (!stop && (node = nodeStack.shift())) {
      if (node.nodeType === Node.TEXT_NODE) {
        const textLength = (node as Text).length;
        if (!foundStart && charIndex.index + textLength >= start) {
          // Set start
          range.setStart(node, start - charIndex.index);
          foundStart = true;
        }
        if (foundStart && charIndex.index + textLength >= end) {
          // Set end
          range.setEnd(node, end - charIndex.index);
          stop = true;
        }
        charIndex.index += textLength;
      } else {
        nodeStack.unshift(...(node.childNodes as any));
      }
    }

    const sel = window.getSelection();
    if (sel) {
      sel.removeAllRanges();
      sel.addRange(range);
    }
  }
}
