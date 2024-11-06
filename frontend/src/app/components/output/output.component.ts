import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-output',
  standalone: true,
  imports: [FormsModule,CommonModule],
  templateUrl: './output.component.html',
  styleUrl: './output.component.css'
})
export class OutputComponent {
  @Input() outputText: string = '';  // Ontvangt de gegenereerde tekst van de parent
  @Input() showMessage: boolean = false;  // Nieuwe input om te bepalen wanneer de boodschap zichtbaar is
  @Output() outputTextChange = new EventEmitter<string>();
  @Output() finalized = new EventEmitter<void>();

  onTextChange(value: string): void {
    this.outputTextChange.emit(value);
  }

  finalizeText() {
    this.finalized.emit();
  }
}
