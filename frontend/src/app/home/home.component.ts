import { Component, ElementRef, ViewChild, ViewEncapsulation } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { ApiService } from '../api/api.service';
import { CommonModule } from '@angular/common';
import { Validators } from '@angular/forms';

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
  @ViewChild('generatedTextDiv') generatedTextDiv!: ElementRef;
  
  textForm: FormGroup;
  private currentRawTextId?: string;
  private currentSuggestionId?: string;
  suggestions: Correction[] = [];
  private originalResponseText: string = '';
  isLoading: boolean = false;
  showMediumTypeError: boolean = false;

  private lastChangePosition: { start: number, end: number } | null = null;

  tooltipVisible = false;
  tooltipX = 0;
  tooltipY = 0;
  currentTooltipSuggestion: Correction | null = null;
  currentTooltipSuggestions: Correction[] = [];

  private changedPositions: { start: number, end: number }[] = [];

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
    private apiService: ApiService
  ) {
    this.textForm = this.formBuilder.group({
      inputText: [''],
      outputText: [''],
      mediumType: ['', Validators.required],
    });

    let text = localStorage.getItem('textInput');
    if (text != null) {
      this.textInput = text;
    }
  }

  shouldShowError(controlName: string): boolean {
    const control = this.textForm.get(controlName);
    if (!control) return false;
    return control.invalid && (control.touched || control.dirty || this.showMediumTypeError);
  }

  async onGenerate() {
    const inputText = this.textForm.get('inputText')?.value;
    let mediumType = this.textForm.get('mediumType')?.value;

    this.showMediumTypeError = true;

    if (!inputText || !mediumType) {
      console.error('Please fill in both text and medium type');
      return;
    }

    this.showMediumTypeError = false;

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
  // Ensure we have unique suggestions based on their positions
  const uniqueSuggestions = suggestions.reduce((acc: Correction[], curr: Correction) => {
    const exists = acc.find(s => 
      s.info.startPos === curr.info.startPos && 
      s.info.endPos === curr.info.endPos
    );
    if (!exists) {
      acc.push(curr);
    }
    return acc;
  }, []);

  this.currentTooltipSuggestions = uniqueSuggestions;

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
      this.rejectSuggestionById(index.toString());
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
        this.changedPositions = [];
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

    // Add the changed position
    this.changedPositions.push({
      start: startPos,
      end: startPos + suggestion.corrected_part.length
    });

    // Adjust existing change positions if they come after this change
    const offsetDifference = suggestion.corrected_part.length - suggestion.incorrect_part.length;
    for (let change of this.changedPositions) {
      if (change.start > endPos) {
        change.start += offsetDifference;
        change.end += offsetDifference;
      }
    }

    this.originalResponseText = newText;

    this.suggestions.splice(index, 1);

    // Adjust suggestions positions
    this.suggestions = this.suggestions.filter((currentSuggestion) => {
      const cStart = currentSuggestion.info.startPos;
      const cEnd = currentSuggestion.info.endPos;
      const isOverlapping =
        (cStart >= startPos && cStart < endPos) ||
        (cEnd > startPos && cEnd <= endPos) ||
        (cStart <= startPos && cEnd >= endPos);

      return !isOverlapping;
    });

    for (const currentSuggestion of this.suggestions) {
      if (currentSuggestion.info.startPos > startPos) {
        currentSuggestion.info.startPos += offsetDifference;
        currentSuggestion.info.endPos += offsetDifference;
      }
    }

    this.renderHighlightedText();
}

onGeneratedTextChange(event: Event) {
  const div = this.generatedTextDiv.nativeElement;
  const newText = div.innerText;
  const oldText = this.originalResponseText;

  if (newText === oldText) return;

  const savedRange = this.saveSelection(div);

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

  // Update changed positions for manual edits
  const manualChangePos = {
    start: changeStart,
    end: changeStart + addedLength
  };

  if (addedLength > 0) {
    this.changedPositions.push(manualChangePos);
  }

  // Adjust existing change positions
  this.changedPositions = this.changedPositions
    .filter(pos => !(pos.end <= changeStart || pos.start >= changeEnd))
    .map(pos => {
      if (pos.start >= changeEnd) {
        return {
          start: pos.start + offsetDifference,
          end: pos.end + offsetDifference
        };
      }
      return pos;
    });

  // Update suggestions positions
  this.suggestions = this.suggestions.filter(suggestion => {
    const sStart = suggestion.info.startPos;
    const sEnd = suggestion.info.endPos;
    const overlaps = !(sEnd <= changeStart || sStart >= changeEnd);
    return !overlaps;
  });

  for (const suggestion of this.suggestions) {
    if (suggestion.info.startPos >= changeEnd) {
      suggestion.info.startPos += offsetDifference;
      suggestion.info.endPos += offsetDifference;
    }
  }

  this.renderHighlightedText();
  this.restoreSelection(div, savedRange);
}

private renderHighlightedText() {
  const div = this.generatedTextDiv.nativeElement;
  const savedRange = this.saveSelection(div);
  div.innerHTML = '';

  const text = this.originalResponseText;

  if (this.suggestions.length === 0 && this.changedPositions.length === 0) {
    div.appendChild(document.createTextNode(text));
    this.restoreSelection(div, savedRange);
    return;
  }

  let currentIndex = 0;

  // Function to process text up to a certain position
  const processTextUpTo = (endPos: number) => {
    if (currentIndex < endPos) {
      let pos = currentIndex;
      while (pos < endPos) {
        const change = this.changedPositions.find(c => c.start >= pos && c.start < endPos);
        if (!change) {
          div.appendChild(document.createTextNode(text.substring(pos, endPos)));
          break;
        }

        if (change.start > pos) {
          div.appendChild(document.createTextNode(text.substring(pos, change.start)));
        }

        const changedSpan = document.createElement('span');
        changedSpan.classList.add('changed-text');
        changedSpan.textContent = text.substring(change.start, change.end);
        div.appendChild(changedSpan);

        pos = change.end;
      }
      currentIndex = endPos;
    }
  };

  // Merge overlapping suggestions
  let mergedIntervals: { start: number; end: number; suggestions: Correction[] }[] = [];
  
  // Sort suggestions by start position
  const sortedSuggestions = [...this.suggestions].sort((a, b) => a.info.startPos - b.info.startPos);
  
  for (const suggestion of sortedSuggestions) {
    const currentInterval = {
      start: suggestion.info.startPos,
      end: suggestion.info.endPos,
      suggestions: [suggestion]
    };

    // Find any existing interval that overlaps with the current suggestion
    const overlappingIndex = mergedIntervals.findIndex(interval => 
      !(interval.end <= currentInterval.start || interval.start >= currentInterval.end)
    );

    if (overlappingIndex === -1) {
      // No overlap, add as new interval
      mergedIntervals.push(currentInterval);
    } else {
      // Merge with existing interval
      const existing = mergedIntervals[overlappingIndex];
      existing.start = Math.min(existing.start, currentInterval.start);
      existing.end = Math.max(existing.end, currentInterval.end);
      existing.suggestions.push(suggestion);
    }
  }

  // Sort merged intervals by start position
  mergedIntervals.sort((a, b) => a.start - b.start);

  // Process merged intervals with their highlights
  for (const interval of mergedIntervals) {
    processTextUpTo(interval.start);

    const span = document.createElement('span');
    span.classList.add('highlight-suggestion');
    span.textContent = text.substring(interval.start, interval.end);

    const mouseEnterListener = (event: Event) => this.showTooltipForMultiple(event, interval.suggestions);
    const mouseLeaveListener = (event: Event) => this.onHighlightMouseLeave(event);
    span.addEventListener('mouseenter', mouseEnterListener);
    span.addEventListener('mouseleave', mouseLeaveListener);

    div.appendChild(span);
    currentIndex = interval.end;
  }

  // Process any remaining text
  processTextUpTo(text.length);

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
