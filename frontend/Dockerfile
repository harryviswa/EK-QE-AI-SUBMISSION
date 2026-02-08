FROM node:18-alpine

WORKDIR /app

# Install curl for healthcheck
RUN apk add --no-cache curl

# Copy package files
COPY package.json package-lock.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build the app
RUN npm run build

# Use a lightweight server
RUN npm install -g serve

EXPOSE 3000

# Start the app
CMD ["serve", "-s", "dist", "-l", "3000"]
