import { HttpClientModule } from '@angular/common/http';
import { TestBed } from '@angular/core/testing';
import { AppRoutingModule } from '../app-routing.module';

import { GoalService } from './goal.service';

describe('GoalService', () => {
  let service: GoalService;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [
        AppRoutingModule,
        HttpClientModule
      ]
    });
    service = TestBed.inject(GoalService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
