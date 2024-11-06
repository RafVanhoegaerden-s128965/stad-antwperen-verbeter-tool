import { Component } from '@angular/core';
import { FormsModule, NgModel } from '@angular/forms';
import { TextInputComponent } from "../components/text-input/text-input.component";
import { MediumSelectComponent } from "../components/medium-select/medium-select.component";
import { OutputComponent } from "../components/output/output.component";
import { EventEmitter, Output } from '@angular/core';


@Component({
  selector: 'app-text-editor',
  standalone: true,
  imports: [FormsModule, TextInputComponent, MediumSelectComponent, OutputComponent],
  templateUrl: './text-editor.component.html',
  styleUrl: './text-editor.component.css'
})
export class TextEditorComponent {
  inputText: string = '';
  selectedMedium: string = '';

  @Output() textGenerated = new EventEmitter<string>();

  onTextChanged(text: string) {
    this.inputText = text;
  }

  onMediumSelected(medium: string) {
    this.selectedMedium = medium;
  }

  generateText() {
    const result = `${this.selectedMedium} ${this.inputText}`;
    this.textGenerated.emit(result);
  }

}