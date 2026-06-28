/**
 * iOSLENS REST API client for Node.js
 */
export class IOSLensClient {
  private baseUrl: string;
  private apiKey: string;

  constructor(
    baseUrl: string = "https://api.ioslens.ai",
    apiKey: string = ""
  ) {
    this.baseUrl = baseUrl.replace(/\/$/, "");
    this.apiKey = apiKey;
  }

  private get headers(): Record<string, string> {
    return {
      "Content-Type": "application/json",
      Authorization: "Bearer " + this.apiKey,
    };
  }

  async health(): Promise<Record<string, unknown>> {
    const res = await fetch(`${this.baseUrl}/health`, {
      headers: this.headers,
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  }

  async evaluateGovernance(params: {
    resourceType: string;
    action: string;
    resourceId?: string;
    purpose?: string;
  }): Promise<Record<string, unknown>> {
    const res = await fetch(`${this.baseUrl}/v1/governance/evaluate`, {
      method: "POST",
      headers: this.headers,
      body: JSON.stringify({
        resource_type: params.resourceType,
        action: params.action,
        resource_id: params.resourceId,
        purpose: params.purpose ?? "",
      }),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  }

  async resolveUDM(params: {
    cipCode?: string;
    socCode?: string;
    naicsCode?: string;
  }): Promise<Record<string, unknown>> {
    const query = new URLSearchParams();
    if (params.cipCode) query.set("cip_code", params.cipCode);
    if (params.socCode) query.set("soc_code", params.socCode);
    if (params.naicsCode) query.set("naics_code", params.naicsCode);

    const res = await fetch(`${this.baseUrl}/v1/udm/resolve?${query}`, {
      headers: this.headers,
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  }
}
