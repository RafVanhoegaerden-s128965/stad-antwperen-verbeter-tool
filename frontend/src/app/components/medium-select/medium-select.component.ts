import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Input, Output, EventEmitter } from '@angular/core';


@Component({
  selector: 'app-medium-select',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './medium-select.component.html',
  styleUrl: './medium-select.component.css'
})
export class MediumSelectComponent {

  @Input() selectedMedium: string = 'Website';
  @Output() selectedMediumChange = new EventEmitter<string>();
  @Input() media: string[] = [];

  onSelectChange(value: string): void {
    this.selectedMediumChange.emit(value);
  }

}
