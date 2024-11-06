import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Input, Output, EventEmitter } from '@angular/core';

@Component({
  selector: 'app-text-input',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './text-input.component.html',
  styleUrl: './text-input.component.css'
})
export class TextInputComponent {

  @Input() inputText: string = '';
  @Output() inputTextChange = new EventEmitter<string>();

  onTextChange(value: string): void {
    this.inputTextChange.emit(value);
  }
}
