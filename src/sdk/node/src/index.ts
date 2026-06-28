// iOSLENS Node.js SDK — public API

export { IOSLensClient } from './client';
export { MCPClient } from './mcp-client';

// Request / response types
export interface GovernanceCheckRequest {
  resource_type: string;
  resource_id?: string;
  purpose: string;
  action?: string;
}

export interface GovernanceCheckResponse {
  allowed: boolean;
  policy_id?: string;
  rationale?: string;
  reason?: string;
  execution_token?: string;
}

export interface UDMResolveRequest {
  query: string;
  systems?: string[];
  limit?: number;
}

export interface UDMResolveResponse {
  results: Array<{
    system: string;
    code: string;
    title: string;
    score?: number;
  }>;
}
