
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nexora-web
spec:
  replicas: 1
  selector:
    matchLabels:
      app: nexora-web
  template:
    metadata:
      labels:
        app: nexora-web
    spec:
      containers:
        - name: nexora-web
          image: __IMAGE__
          imagePullPolicy: Always
          ports:
            - containerPort: 5000
          env:
            - name: PORT
              value: "5000"
            - name: NEXORA_DESKTOP_ENABLED
              value: "false"
            - name: FLASK_SECRET_KEY
              valueFrom:
                secretKeyRef:
                  name: nexora-secrets
                  key: FLASK_SECRET_KEY
          volumeMounts:
            - name: database-storage
              mountPath: /app/database
          readinessProbe:
            httpGet:
              path: /healthz
              port: 5000
            initialDelaySeconds: 5
            periodSeconds: 10
          livenessProbe:
            httpGet:
              path: /healthz
              port: 5000
            initialDelaySeconds: 15
            periodSeconds: 20
      volumes:
        - name: database-storage
          persistentVolumeClaim:
            claimName: nexora-db-pvc
