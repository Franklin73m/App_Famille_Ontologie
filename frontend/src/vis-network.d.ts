// Déclaration minimale de la bibliothèque de graphe : le projet compile ainsi
// quelle que soit la version des typages fournis par vis-network.
declare module 'vis-network/standalone' {
  export class Network {
    constructor(container: HTMLElement, data: any, options?: any);
    destroy(): void;
    fit(): void;
  }
}
