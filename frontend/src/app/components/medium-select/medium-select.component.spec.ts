import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MediumSelectComponent } from './medium-select.component';

describe('MediumSelectComponent', () => {
  let component: MediumSelectComponent;
  let fixture: ComponentFixture<MediumSelectComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MediumSelectComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(MediumSelectComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
