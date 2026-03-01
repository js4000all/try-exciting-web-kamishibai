/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ChoiceResult } from './ChoiceResult';
import type { LogEntry } from './LogEntry';
import type { Position } from './Position';
import type { RngState } from './RngState';
import type { ScenarioRef } from './ScenarioRef';
export type SaveDataV0 = {
    state_version: string;
    scenario_ref: ScenarioRef;
    position: Position;
    variables: Record<string, (string | number | boolean | null)>;
    read_history?: Array<string>;
    log?: Array<LogEntry>;
    choice_results?: Array<ChoiceResult>;
    rng: RngState;
};

