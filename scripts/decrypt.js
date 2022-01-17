/**
 * Decrypt functie aan de ontvangende zijde (Subsidie portaal)
 */
const Buffer = require("buffer").Buffer;
const crypto = require("crypto");

function decrypt(encryptedValue, secretKey) {
  const keyBuffer = Buffer.from(secretKey);

  const decodedBuffer = Buffer.from(encryptedValue, "base64");
  const ivBuffer = decodedBuffer.slice(0, 16);
  const dataBuffer = decodedBuffer.slice(16);

  const decipheriv = crypto.createDecipheriv(
    "aes-128-cbc",
    keyBuffer,
    ivBuffer
  );
  return decipheriv.update(dataBuffer).toString() + decipheriv.final("utf-8");
}

identifier = "123123123";

payload = "";
secretKey = "";

console.log(decrypt(payload, secretKey));
